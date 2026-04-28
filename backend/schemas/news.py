"""
News Response Schemas

Pydantic models for news API responses with proper serialization and documentation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class NewsArticleResponse(BaseModel):
    """News article in list response"""
    
    id: str = Field(..., description="Unique article ID")
    title: str = Field(..., description="Article title")
    content: Optional[str] = Field(None, description="Article content/summary")
    source: str = Field(..., description="News source (NewsAPI, NASA, etc.)")
    source_url: str = Field(..., description="URL to original article")
    image_url: Optional[str] = Field(None, description="Article thumbnail image URL")
    published_at: datetime = Field(..., description="Publication timestamp")
    is_stem_relevant: bool = Field(default=False, description="Whether article is STEM-related")
    is_breaking_news: bool = Field(default=False, description="Whether this is breaking news")
    stem_confidence: float = Field(default=0.0, ge=0, le=1, description="STEM relevance confidence (0-1)")
    topics: List[str] = Field(default=[], description="Extracted STEM topics")
    view_count: int = Field(default=0, description="Number of times article was viewed")
    created_at: datetime = Field(..., description="When article was added to system")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "news_123",
                "title": "New Quantum Computing Breakthrough",
                "source": "NewsAPI",
                "source_url": "https://example.com/article",
                "published_at": "2026-04-22T10:30:00Z",
                "is_stem_relevant": True,
                "is_breaking_news": True,
                "stem_confidence": 0.95,
                "topics": ["physics", "technology", "data"],
                "view_count": 1250,
                "created_at": "2026-04-22T11:00:00Z",
            }
        }


class NewsArticleDetailResponse(NewsArticleResponse):
    """Detailed news article response with full content"""
    
    content: str = Field(..., description="Full article content")
    author: Optional[str] = Field(None, description="Article author")
    keywords: List[str] = Field(default=[], description="Article keywords")
    sentiment: Optional[str] = Field(None, description="Sentiment analysis result (positive/negative/neutral)")
    engagement_score: float = Field(default=0.0, description="Calculated engagement score")
    related_lessons: List[str] = Field(default=[], description="IDs of lessons generated from this article")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "news_123",
                "title": "New Quantum Computing Breakthrough",
                "content": "Full article content here...",
                "source": "NewsAPI",
                "source_url": "https://example.com/article",
                "author": "Jane Scientist",
                "published_at": "2026-04-22T10:30:00Z",
                "is_stem_relevant": True,
                "is_breaking_news": True,
                "stem_confidence": 0.95,
                "topics": ["physics", "technology"],
                "keywords": ["quantum", "computing", "breakthrough"],
                "sentiment": "positive",
                "view_count": 1250,
                "engagement_score": 8.7,
                "related_lessons": ["lesson_456", "lesson_789"],
                "created_at": "2026-04-22T11:00:00Z",
            }
        }


class NewsListResponse(BaseModel):
    """Paginated list of news articles"""
    
    items: List[NewsArticleResponse] = Field(..., description="Array of news articles")
    total: int = Field(..., ge=0, description="Total number of articles matching query")
    limit: int = Field(..., ge=1, description="Number of items per page")
    offset: int = Field(..., ge=0, description="Number of items skipped")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "news_123",
                        "title": "Quantum Computing Breakthrough",
                        "source": "NewsAPI",
                        "published_at": "2026-04-22T10:30:00Z",
                        "is_stem_relevant": True,
                        "topics": ["physics", "technology"],
                    }
                ],
                "total": 150,
                "limit": 50,
                "offset": 0,
            }
        }


class BreakingNewsResponse(BaseModel):
    """Response for breaking news endpoint"""
    
    items: List[NewsArticleResponse] = Field(..., description="Breaking news articles")
    count: int = Field(..., ge=0, description="Number of breaking news articles")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "news_123",
                        "title": "Major Scientific Discovery",
                        "is_breaking_news": True,
                        "topics": ["biology", "science"],
                    }
                ],
                "count": 1,
            }
        }


class TrendingNewsResponse(BaseModel):
    """Response for trending news endpoint"""
    
    items: List[NewsArticleResponse] = Field(..., description="Trending articles")
    metrics: Dict[str, Any] = Field(..., description="Trend analysis metrics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "news_123",
                        "title": "Most Viewed Article",
                        "view_count": 5000,
                    }
                ],
                "metrics": {
                    "total_articles": 20,
                    "time_period_hours": 24,
                    "avg_views": 1250.5,
                },
            }
        }


class FetchNewsResponse(BaseModel):
    """Response for manual news fetch endpoint"""
    
    total_fetched: int = Field(..., ge=0, description="Total articles retrieved from sources")
    new_articles: int = Field(..., ge=0, description="Number of newly added articles")
    stem_articles: int = Field(..., ge=0, description="Number of STEM-relevant articles")
    timestamp: datetime = Field(..., description="When the fetch operation completed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_fetched": 450,
                "new_articles": 120,
                "stem_articles": 87,
                "timestamp": "2026-04-22T12:00:00Z",
            }
        }


class NewsStatsResponse(BaseModel):
    """Statistics about news in the system"""
    
    total_articles: int = Field(..., description="Total articles in database")
    stem_articles: int = Field(..., description="STEM-relevant articles")
    breaking_articles: int = Field(..., description="Breaking news count")
    articles_last_24h: int = Field(..., description="Articles added in last 24 hours")
    avg_stem_confidence: float = Field(..., ge=0, le=1, description="Average STEM confidence score")
    top_topics: List[str] = Field(..., description="Most common STEM topics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_articles": 5000,
                "stem_articles": 3500,
                "breaking_articles": 12,
                "articles_last_24h": 350,
                "avg_stem_confidence": 0.82,
                "top_topics": ["physics", "technology", "biology"],
            }
        }


# Request body schemas

class NewsFilterParams(BaseModel):
    """Parameters for filtering news"""
    
    stem_only: bool = Field(default=True, description="Filter for STEM articles")
    topics: Optional[List[str]] = Field(None, description="Filter by topics")
    breaking_only: bool = Field(default=False, description="Only breaking news")
    min_confidence: float = Field(default=0.0, ge=0, le=1, description="Minimum STEM confidence")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stem_only": True,
                "topics": ["physics", "chemistry"],
                "breaking_only": False,
                "min_confidence": 0.7,
            }
        }
