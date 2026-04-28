"""
News Aggregator Service

Fetches news from multiple sources (NewsAPI, RSS feeds), classifies for STEM relevance,
detects breaking news, and creates NewsArticle objects for database storage.
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

import aiohttp
import feedparser

from config import settings
from models.news import NewsArticle
from ml.classifier import STEMClassifier
from utils.logger import get_logger

logger = get_logger(__name__)


class NewsAggregator:
    """
    Aggregates news from multiple sources and filters for STEM relevance.
    
    Supports:
    - REST APIs (NewsAPI)
    - RSS Feeds (NASA, ScienceDaily, Nature, ArXiv)
    - Concurrent fetching with asyncio
    - ML-based STEM classification
    - Breaking news detection
    """
    
    def __init__(self):
        """Initialize NewsAggregator with STEM classifier and news sources"""
        self.classifier = STEMClassifier()
        self.sources: List[Dict] = []
        self.articles: List[Dict] = []
        self.breaking_articles: List[Dict] = []
        
        # Breaking news keywords
        self.breaking_keywords = [
            "earthquake", "launch", "discovery", "breakthrough",
            "first", "record", "major", "unprecedented", "historic",
            "critical", "emergency", "alert", "urgent"
        ]
        
        logger.info("📰 NewsAggregator initialized")
        self._initialize_sources()
    
    def _initialize_sources(self) -> None:
        """Initialize news sources from multiple platforms"""
        
        # NewsAPI - REST API source
        self.sources.append({
            "name": "NewsAPI",
            "type": "api",
            "url": "https://newsapi.org/v2/everything",
            "api_key": settings.NEWSAPI_KEY,
            "query": "science OR technology OR engineering OR math OR STEM",
            "sort_by": "publishedAt",
            "language": "en",
        })
        
        # NASA Breaking News - RSS Feed
        self.sources.append({
            "name": "NASA Breaking News",
            "type": "rss",
            "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss",
            "category": "space",
        })
        
        # ScienceDaily - RSS Feed
        self.sources.append({
            "name": "ScienceDaily",
            "type": "rss",
            "url": "https://www.sciencedaily.com/rss/all.xml",
            "category": "general_science",
        })
        
        # Nature News - RSS Feed
        self.sources.append({
            "name": "Nature News",
            "type": "rss",
            "url": "https://www.nature.com/nature.rss",
            "category": "research",
        })
        
        # ArXiv Computer Science - RSS Feed
        self.sources.append({
            "name": "ArXiv CS",
            "type": "rss",
            "url": "http://export.arxiv.org/rss/cs",
            "category": "ai_ml",
        })
        
        logger.info(f"✅ Initialized {len(self.sources)} news sources")
    
    async def fetch_all_news(self) -> List[NewsArticle]:
        """
        Fetch news from all sources concurrently and filter for STEM relevance.
        
        Returns:
            List of NewsArticle objects with STEM relevance filtering
        """
        logger.info("🔄 Starting news aggregation from all sources...")
        
        try:
            # Create fetch tasks for all sources
            tasks = [
                self._fetch_from_source(source)
                for source in self.sources
            ]
            
            # Execute all fetch tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Aggregate results
            self.articles = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"❌ Error fetching news: {result}")
                elif isinstance(result, list):
                    self.articles.extend(result)
            
            logger.info(f"📊 Fetched {len(self.articles)} total articles")
            
            # Filter for STEM relevance
            await self._filter_stem_articles()
            
            # Detect breaking news
            await self.detect_breaking_news()
            
            logger.info(f"✅ News aggregation complete: {len(self.articles)} STEM articles, {len(self.breaking_articles)} breaking")
            
            return self._convert_to_newsarticles()
        
        except Exception as e:
            logger.error(f"❌ Fatal error in fetch_all_news: {e}", exc_info=True)
            return []
    
    async def _fetch_from_source(self, source: Dict) -> List[Dict]:
        """
        Fetch from a single source based on type.
        
        Args:
            source: Source configuration dictionary
            
        Returns:
            List of article dictionaries
        """
        try:
            if source["type"] == "api":
                return await self._fetch_from_api(source)
            elif source["type"] == "rss":
                return await self._fetch_from_rss(source)
            else:
                logger.warning(f"⚠️ Unknown source type: {source['type']}")
                return []
        
        except Exception as e:
            logger.error(f"❌ Error fetching from {source.get('name', 'unknown')}: {e}")
            return []
    
    async def _fetch_from_api(self, source: Dict) -> List[Dict]:
        """
        Fetch news from REST API (NewsAPI).
        
        Args:
            source: API source configuration
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                params = {
                    "q": source.get("query", "STEM"),
                    "sortBy": source.get("sort_by", "publishedAt"),
                    "language": source.get("language", "en"),
                    "apiKey": source.get("api_key"),
                    "pageSize": 100,
                }
                
                async with session.get(source["url"], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get("articles", []):
                            article = {
                                "source": source["name"],
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "description": item.get("description", ""),
                                "content": item.get("content", ""),
                                "image_url": item.get("urlToImage", ""),
                                "published_at": self._parse_datetime(item.get("publishedAt")),
                                "source_url": item.get("source", {}).get("url", ""),
                            }
                            articles.append(article)
                        
                        logger.info(f"✅ Fetched {len(articles)} articles from {source['name']}")
                    else:
                        logger.warning(f"⚠️ {source['name']} API returned status {response.status}")
        
        except asyncio.TimeoutError:
            logger.error(f"❌ Timeout fetching from {source['name']}")
        except Exception as e:
            logger.error(f"❌ Error fetching from API {source['name']}: {e}")
        
        return articles
    
    async def _fetch_from_rss(self, source: Dict) -> List[Dict]:
        """
        Fetch news from RSS feed using feedparser.
        
        Args:
            source: RSS source configuration
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(source["url"]) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        for entry in feed.entries[:100]:  # Limit to 100 entries
                            # Extract publication date
                            published_at = None
                            if hasattr(entry, "published_parsed"):
                                published_at = datetime(*entry.published_parsed[:6])
                            elif hasattr(entry, "updated_parsed"):
                                published_at = datetime(*entry.updated_parsed[:6])
                            else:
                                published_at = datetime.utcnow()
                            
                            article = {
                                "source": source["name"],
                                "title": entry.get("title", ""),
                                "url": entry.get("link", ""),
                                "description": entry.get("summary", ""),
                                "content": entry.get("content", [{}])[0].get("value", "") if hasattr(entry, "content") else "",
                                "image_url": self._extract_image_from_rss(entry),
                                "published_at": published_at,
                                "source_url": source["url"],
                            }
                            articles.append(article)
                        
                        logger.info(f"✅ Fetched {len(articles)} articles from RSS feed {source['name']}")
                    else:
                        logger.warning(f"⚠️ RSS feed {source['name']} returned status {response.status}")
        
        except asyncio.TimeoutError:
            logger.error(f"❌ Timeout fetching RSS from {source['name']}")
        except Exception as e:
            logger.error(f"❌ Error fetching RSS from {source['name']}: {e}")
        
        return articles
    
    async def _filter_stem_articles(self) -> None:
        """
        Filter articles by STEM relevance using ML classifier.
        
        Keeps only articles with STEM confidence > 0.7
        """
        logger.info("🧠 Filtering articles for STEM relevance...")
        
        filtered_articles = []
        
        for article in self.articles:
            try:
                # Create classification input
                text_to_classify = f"{article.get('title', '')} {article.get('description', '')}"
                
                # Get STEM confidence score
                is_stem, confidence, topics = self.classifier.classify(text_to_classify)
                
                # Keep article if confidence > 0.7
                if is_stem and confidence > 0.7:
                    article["is_stem_relevant"] = True
                    article["stem_confidence"] = confidence
                    article["topics"] = topics
                    filtered_articles.append(article)
                else:
                    logger.debug(f"⊘ Filtered out: {article['title'][:50]}... (confidence: {confidence:.2f})")
            
            except Exception as e:
                logger.error(f"❌ Error classifying article: {e}")
        
        self.articles = filtered_articles
        logger.info(f"✅ Filtered to {len(self.articles)} STEM-relevant articles")
    
    async def detect_breaking_news(self) -> None:
        """
        Detect and flag breaking news articles.
        
        Criteria:
        - Published in last 1 hour
        - Contains breaking news keywords
        """
        logger.info("🚨 Detecting breaking news...")
        
        self.breaking_articles = []
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        for article in self.articles:
            try:
                published_at = article.get("published_at")
                
                # Check if published recently (within 1 hour)
                if published_at and published_at > one_hour_ago:
                    title_lower = article.get("title", "").lower()
                    description_lower = article.get("description", "").lower()
                    content_lower = article.get("content", "").lower()
                    
                    # Check for breaking keywords
                    is_breaking = any(
                        keyword in title_lower or
                        keyword in description_lower or
                        keyword in content_lower
                        for keyword in self.breaking_keywords
                    )
                    
                    if is_breaking:
                        article["breaking_news"] = True
                        self.breaking_articles.append(article)
                        logger.warning(f"🚨 BREAKING NEWS: {article['title']}")
                    else:
                        article["breaking_news"] = False
                else:
                    article["breaking_news"] = False
            
            except Exception as e:
                logger.error(f"❌ Error detecting breaking news: {e}")
                article["breaking_news"] = False
        
        logger.info(f"✅ Detected {len(self.breaking_articles)} breaking news articles")
    
    def _convert_to_newsarticles(self) -> List[NewsArticle]:
        """
        Convert article dictionaries to NewsArticle ORM objects.
        
        Returns:
            List of NewsArticle objects ready for database insertion
        """
        newsarticles = []
        
        for article in self.articles:
            try:
                newsarticle = NewsArticle(
                    title=article.get("title", "")[:500],
                    url=article.get("url", ""),
                    description=article.get("description", ""),
                    content=article.get("content", ""),
                    source=article.get("source", "Unknown"),
                    source_url=article.get("source_url", ""),
                    image_url=article.get("image_url", ""),
                    published_at=article.get("published_at", datetime.utcnow()),
                    scraped_at=datetime.utcnow(),
                    is_stem_relevant=article.get("is_stem_relevant", False),
                    stem_confidence=article.get("stem_confidence", 0.0),
                    topics=article.get("topics", []),
                    breaking_news=article.get("breaking_news", False),
                    category="STEM",
                )
                newsarticles.append(newsarticle)
            
            except Exception as e:
                logger.error(f"❌ Error converting article to NewsArticle: {e}")
        
        return newsarticles
    
    def _parse_datetime(self, date_string: Optional[str]) -> datetime:
        """
        Parse ISO 8601 datetime string from NewsAPI.
        
        Args:
            date_string: ISO 8601 formatted datetime string
            
        Returns:
            Parsed datetime object or current UTC time if parsing fails
        """
        if not date_string:
            return datetime.utcnow()
        
        try:
            # Try ISO 8601 format: 2024-04-22T10:30:00Z
            if date_string.endswith('Z'):
                return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return datetime.fromisoformat(date_string)
        
        except Exception as e:
            logger.warning(f"⚠️ Could not parse datetime '{date_string}': {e}")
            return datetime.utcnow()
    
    def _extract_image_from_rss(self, entry) -> str:
        """
        Extract image URL from RSS feed entry.
        
        Args:
            entry: RSS feed entry object
            
        Returns:
            Image URL or empty string
        """
        try:
            # Check for media:content
            if hasattr(entry, "media_content"):
                return entry.media_content[0].get("url", "")
            
            # Check for media:thumbnail
            if hasattr(entry, "media_thumbnail"):
                return entry.media_thumbnail[0].get("url", "")
            
            # Check for image tag
            if hasattr(entry, "image"):
                return entry.image.get("url", "")
            
            return ""
        
        except Exception as e:
            logger.debug(f"⚠️ Could not extract image from RSS entry: {e}")
            return ""


# Singleton instance
news_aggregator = NewsAggregator()
