"""
News API Endpoints

Provides endpoints for fetching, filtering, and managing educational news articles.
Integrates with the news aggregator service for STEM content.
"""
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from config import settings
from utils.logger import get_logger
from database import get_db
from models.news import NewsArticle
from services.news_aggregator import news_aggregator
from schemas.news import (
    NewsArticleResponse,
    NewsArticleDetailResponse,
    NewsListResponse,
    BreakingNewsResponse,
    TrendingNewsResponse,
    FetchNewsResponse,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get(
    "",
    response_model=NewsListResponse,
    summary="Get news articles",
    description="Retrieve paginated list of news articles with optional STEM filtering",
)
async def get_news_list(
    limit: int = Query(50, ge=1, le=500, description="Number of articles to return"),
    offset: int = Query(0, ge=0, description="Number of articles to skip"),
    stem_only: bool = Query(True, description="Filter for STEM-relevant articles only"),
    db: Session = Depends(get_db),
) -> NewsListResponse:
    """
    Get paginated list of news articles.
    
    Query Parameters:
    - limit: Number of articles (1-500, default 50)
    - offset: Articles to skip (default 0)
    - stem_only: Filter for STEM content (default True)
    
    Returns:
    - List of articles sorted by publication date (newest first)
    - Total count and pagination info
    """
    logger.info(f"📰 Fetching news articles: limit={limit}, offset={offset}, stem_only={stem_only}")
    
    try:
        query = db.query(NewsArticle)
        
        # Filter by STEM relevance
        if stem_only:
            query = query.filter(NewsArticle.is_stem_relevant == True)
            logger.debug("🔬 Filtering for STEM-relevant articles")
        
        # Get total count
        total = query.count()
        
        # Apply ordering and pagination
        articles = query.order_by(desc(NewsArticle.published_at)).offset(offset).limit(limit).all()
        
        logger.info(f"✅ Retrieved {len(articles)} articles (total: {total})")
        
        return NewsListResponse(
            items=[NewsArticleResponse.from_orm(article) for article in articles],
            total=total,
            limit=limit,
            offset=offset,
        )
    
    except Exception as e:
        logger.error(f"❌ Error fetching news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch news articles")


@router.get(
    "/{news_id}",
    response_model=NewsArticleDetailResponse,
    summary="Get news article detail",
    description="Retrieve a single news article by ID",
    responses={404: {"description": "Article not found"}},
)
async def get_news_detail(
    news_id: str = Query(..., description="News article ID"),
    db: Session = Depends(get_db),
) -> NewsArticleDetailResponse:
    """
    Get detailed information about a specific news article.
    
    Path Parameters:
    - news_id: Unique identifier of the article
    
    Returns:
    - Complete article information including content, metadata, and engagement
    """
    logger.info(f"📰 Fetching article detail: {news_id}")
    
    try:
        article = db.query(NewsArticle).filter(NewsArticle.id == news_id).first()
        
        if not article:
            logger.warning(f"⚠️ Article not found: {news_id}")
            raise HTTPException(status_code=404, detail=f"Article {news_id} not found")
        
        logger.info(f"✅ Retrieved article: {article.title[:50]}...")
        
        return NewsArticleDetailResponse.from_orm(article)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching article detail: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch article")


@router.post(
    "/fetch",
    response_model=FetchNewsResponse,
    summary="Fetch new articles",
    description="Manually trigger news fetch from all sources (admin only)",
    responses={
        403: {"description": "Not authorized"},
        500: {"description": "Fetch failed"},
    },
)
async def fetch_news_manually(
    db: Session = Depends(get_db),
) -> FetchNewsResponse:
    """
    Manually trigger news fetching from all sources.
    
    This endpoint:
    - Calls the news aggregator service
    - Fetches from all configured sources (NewsAPI, RSS feeds)
    - Filters for STEM relevance
    - Saves to database
    - Returns count of new articles added
    
    Returns:
    - total_fetched: Total articles retrieved
    - new_articles: Count of newly added articles
    - stem_articles: Count of STEM-relevant articles
    - timestamp: Fetch operation timestamp
    """
    logger.info("🔄 Manual news fetch triggered")
    
    try:
        # TODO: Add authorization check for admin role
        # if not is_admin(current_user):
        #     raise HTTPException(status_code=403, detail="Not authorized")
        
        logger.info("🔍 Calling news aggregator service...")
        articles = await news_aggregator.fetch_all_news()
        
        if not articles:
            logger.warning("⚠️ No articles fetched")
            return FetchNewsResponse(
                total_fetched=0,
                new_articles=0,
                stem_articles=0,
                timestamp=datetime.utcnow(),
            )
        
        logger.info(f"📥 Fetched {len(articles)} articles from sources")
        
        # Save to database
        new_count = 0
        stem_count = 0
        
        for article in articles:
            try:
                # Check if article already exists
                existing = db.query(NewsArticle).filter(
                    NewsArticle.source_url == article.source_url
                ).first()
                
                if not existing:
                    db.add(article)
                    new_count += 1
                    
                    if article.is_stem_relevant:
                        stem_count += 1
            
            except Exception as e:
                logger.warning(f"⚠️ Error saving article: {e}")
                continue
        
        # Commit all articles
        db.commit()
        
        logger.info(
            f"✅ News fetch complete: {new_count} new articles, "
            f"{stem_count} STEM-relevant"
        )
        
        return FetchNewsResponse(
            total_fetched=len(articles),
            new_articles=new_count,
            stem_articles=stem_count,
            timestamp=datetime.utcnow(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error during news fetch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="News fetch failed")


@router.get(
    "/breaking",
    response_model=BreakingNewsResponse,
    summary="Get breaking news",
    description="Retrieve latest breaking news articles",
)
async def get_breaking_news(
    limit: int = Query(10, ge=1, le=50, description="Number of articles to return"),
    db: Session = Depends(get_db),
) -> BreakingNewsResponse:
    """
    Get the latest breaking news articles.
    
    Query Parameters:
    - limit: Number of articles (1-50, default 10)
    
    Returns:
    - List of breaking news articles sorted by publication date (newest first)
    - All articles must be marked as breaking news
    """
    logger.info(f"🚨 Fetching breaking news (limit={limit})")
    
    try:
        articles = (
            db.query(NewsArticle)
            .filter(
                and_(
                    NewsArticle.is_breaking_news == True,
                    NewsArticle.is_stem_relevant == True,
                )
            )
            .order_by(desc(NewsArticle.published_at))
            .limit(limit)
            .all()
        )
        
        logger.info(f"✅ Found {len(articles)} breaking news articles")
        
        return BreakingNewsResponse(
            items=[NewsArticleResponse.from_orm(article) for article in articles],
            count=len(articles),
        )
    
    except Exception as e:
        logger.error(f"❌ Error fetching breaking news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch breaking news")


@router.get(
    "/trending",
    response_model=TrendingNewsResponse,
    summary="Get trending news",
    description="Retrieve most viewed/engaged articles from the last 24 hours",
)
async def get_trending_news(
    limit: int = Query(20, ge=1, le=100, description="Number of articles to return"),
    hours: int = Query(24, ge=1, le=168, description="Look back period in hours"),
    db: Session = Depends(get_db),
) -> TrendingNewsResponse:
    """
    Get trending news articles based on engagement metrics.
    
    Query Parameters:
    - limit: Number of articles (1-100, default 20)
    - hours: Look-back period in hours (1-168, default 24)
    
    Returns:
    - Articles sorted by engagement/view count
    - Only includes articles from the specified time period
    - Considers lessons generated from articles as engagement metric
    """
    logger.info(f"📈 Fetching trending news (limit={limit}, hours={hours})")
    
    try:
        # Calculate time threshold
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        logger.debug(f"⏰ Looking for articles since: {time_threshold}")
        
        # Query articles with filtering
        articles = (
            db.query(NewsArticle)
            .filter(
                and_(
                    NewsArticle.published_at >= time_threshold,
                    NewsArticle.is_stem_relevant == True,
                )
            )
            .order_by(desc(NewsArticle.view_count))
            .limit(limit)
            .all()
        )
        
        logger.info(f"✅ Found {len(articles)} trending articles")
        
        # Calculate trend metrics
        trend_metrics = {
            "total_articles": len(articles),
            "time_period_hours": hours,
            "avg_views": (
                sum(a.view_count for a in articles) / len(articles)
                if articles
                else 0
            ),
        }
        
        return TrendingNewsResponse(
            items=[NewsArticleResponse.from_orm(article) for article in articles],
            metrics=trend_metrics,
        )
    
    except Exception as e:
        logger.error(f"❌ Error fetching trending news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch trending news")


@router.get(
    "/search",
    response_model=NewsListResponse,
    summary="Search news articles",
    description="Search news articles by keyword or topic",
)
async def search_news(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    stem_only: bool = Query(True),
    db: Session = Depends(get_db),
) -> NewsListResponse:
    """
    Search news articles by title or content.
    
    Query Parameters:
    - q: Search query (required, 1-200 characters)
    - limit: Results per page
    - offset: Results to skip
    - stem_only: Filter for STEM content
    
    Returns:
    - Articles matching search query sorted by relevance
    """
    logger.info(f"🔍 Searching news: q='{q}', limit={limit}, stem_only={stem_only}")
    
    try:
        query = db.query(NewsArticle)
        
        # Search in title and content (case-insensitive)
        search_term = f"%{q.lower()}%"
        query = query.filter(
            (NewsArticle.title.ilike(search_term)) |
            (NewsArticle.content.ilike(search_term))
        )
        
        # STEM filter
        if stem_only:
            query = query.filter(NewsArticle.is_stem_relevant == True)
        
        total = query.count()
        
        articles = (
            query.order_by(desc(NewsArticle.published_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        logger.info(f"✅ Found {len(articles)} matching articles (total: {total})")
        
        return NewsListResponse(
            items=[NewsArticleResponse.from_orm(article) for article in articles],
            total=total,
            limit=limit,
            offset=offset,
        )
    
    except Exception as e:
        logger.error(f"❌ Error searching news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed")
