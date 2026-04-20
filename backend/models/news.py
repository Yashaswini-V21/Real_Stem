"""News and article models for RealSTEM content aggregation"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, JSON, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class NewsArticle(Base):
    """NewsArticle model for STEM-related news and articles
    
    Represents curated news articles from various sources with STEM relevance
    scoring and categorization for the RealSTEM platform.
    """
    __tablename__ = "news_articles"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Article Content
    title = Column(String(500), nullable=False, index=True)
    url = Column(String(500), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=True)  # Full article content
    description = Column(Text, nullable=True)  # Article summary/description
    
    # Source Information
    source = Column(String(200), nullable=False, index=True)  # e.g., 'BBC', 'Science Daily'
    source_url = Column(String(500), nullable=True)  # Original source domain
    image_url = Column(String(500), nullable=True)  # Article thumbnail/header image
    
    # STEM Relevance Classification
    is_stem_relevant = Column(Boolean, nullable=True, default=None, index=True)
    stem_confidence = Column(Float, nullable=True)  # 0.0 to 1.0 confidence score
    topics = Column(JSON, nullable=False, default=list)  # e.g., ['physics', 'chemistry', 'AI']
    
    # Article Classification
    breaking_news = Column(Boolean, default=False, index=True)
    category = Column(String(100), nullable=True, index=True)  # e.g., 'Technology', 'Medicine'
    
    # Timestamps
    published_at = Column(DateTime, nullable=False, index=True)  # Original publication date
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)  # When we fetched it
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # When added to DB
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Engagement & Metadata
    views = Column(Float, default=0)  # Number of views
    engagement_score = Column(Float, nullable=True, default=None)  # Calculated engagement metric
    metadata = Column(JSON, nullable=False, default={})  # Additional metadata
    # metadata structure example:
    # {
    #     "author": "John Doe",
    #     "reading_time_minutes": 5,
    #     "language": "en",
    #     "keywords": ["quantum", "computing"],
    #     "sentiment": "positive",
    #     "media_count": 2,
    #     "external_links": 5
    # }
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_published_at_desc', 'published_at.desc()'),
        Index('idx_stem_relevant_breaking', 'is_stem_relevant', 'breaking_news'),
        Index('idx_source_published', 'source', 'published_at'),
        Index('idx_scraped_at', 'scraped_at'),
        Index('idx_stem_confidence', 'stem_confidence'),
    )
    
    def __repr__(self) -> str:
        """String representation of NewsArticle"""
        return (
            f"<NewsArticle(id={self.id}, title={self.title[:50]}..., "
            f"source={self.source}, stem_relevant={self.is_stem_relevant})>"
        )
    
    def __str__(self) -> str:
        """User-friendly string representation"""
        return f"{self.title} - {self.source}"
    
    @property
    def is_highly_confident_stem(self) -> bool:
        """Check if article is highly confident STEM content
        
        Returns:
            True if STEM relevant with > 0.8 confidence
        """
        return (
            self.is_stem_relevant is True and 
            self.stem_confidence is not None and 
            self.stem_confidence > 0.8
        )
    
    @property
    def is_trending(self) -> bool:
        """Check if article is trending
        
        Returns:
            True if article is breaking news or has high engagement
        """
        return (
            self.breaking_news or 
            (self.engagement_score is not None and self.engagement_score > 0.7)
        )
    
    @property
    def reading_time_minutes(self) -> int:
        """Estimate reading time from content length
        
        Assumes average reading speed of 200 words per minute.
        
        Returns:
            Estimated reading time in minutes
        """
        if not self.content:
            return 0
        word_count = len(self.content.split())
        return max(1, word_count // 200)
    
    def set_metadata(self, key: str, value) -> None:
        """Set a metadata value
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        if not isinstance(self.metadata, dict):
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default=None):
        """Get a metadata value
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        if not isinstance(self.metadata, dict):
            return default
        return self.metadata.get(key, default)
    
    def add_topic(self, topic: str) -> None:
        """Add a topic to the article
        
        Args:
            topic: Topic name to add
        """
        if not isinstance(self.topics, list):
            self.topics = []
        if topic.lower() not in [t.lower() for t in self.topics]:
            self.topics.append(topic.lower())
    
    def remove_topic(self, topic: str) -> None:
        """Remove a topic from the article
        
        Args:
            topic: Topic name to remove
        """
        if isinstance(self.topics, list):
            self.topics = [t for t in self.topics if t.lower() != topic.lower()]
    
    def has_topic(self, topic: str) -> bool:
        """Check if article has a specific topic
        
        Args:
            topic: Topic name to check
            
        Returns:
            True if article has the topic, False otherwise
        """
        if not isinstance(self.topics, list):
            return False
        return topic.lower() in [t.lower() for t in self.topics]
    
    def increment_views(self, count: int = 1) -> None:
        """Increment view count
        
        Args:
            count: Number of views to add (default: 1)
        """
        if self.views is None:
            self.views = 0
        self.views += count
    
    def to_dict(self, include_content: bool = False) -> dict:
        """Convert article to dictionary
        
        Args:
            include_content: Whether to include full content in output
            
        Returns:
            Dictionary representation of article
        """
        article_dict = {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "source": self.source,
            "source_url": self.source_url,
            "image_url": self.image_url,
            "is_stem_relevant": self.is_stem_relevant,
            "stem_confidence": self.stem_confidence,
            "topics": self.topics,
            "breaking_news": self.breaking_news,
            "category": self.category,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "views": self.views,
            "engagement_score": self.engagement_score,
            "reading_time_minutes": self.reading_time_minutes,
            "is_trending": self.is_trending,
            "is_highly_confident_stem": self.is_highly_confident_stem,
        }
        
        if include_content:
            article_dict["content"] = self.content
        
        # Only include metadata if it's not empty
        if self.metadata:
            article_dict["metadata"] = self.metadata
        
        return article_dict

