"""Lesson model for RealSTEM educational content"""
from sqlalchemy import (
    Column, String, Text, DateTime, Integer, Float, Boolean, 
    Enum, JSON, Index, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class LessonStatus(str, enum.Enum):
    """Lesson publication status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Lesson(Base):
    """Lesson model for adaptive STEM educational content
    
    Represents a lesson that can be generated from news articles and
    adapted for multiple educational levels, complete with videos,
    simulations, career connections, and educational standards alignment.
    """
    __tablename__ = "lessons"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Relationships
    news_article_id = Column(
        String, 
        ForeignKey("news_articles.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    created_by = Column(
        String, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    
    # Lesson Metadata
    title = Column(String(500), nullable=False, index=True)
    summary = Column(Text, nullable=True)  # Brief lesson overview
    
    # Multi-Level Content (Adaptive Learning)
    # Each level contains the lesson content adapted for that grade level
    elementary_content = Column(JSON, nullable=True)  # Grades K-5
    middle_school_content = Column(JSON, nullable=True)  # Grades 6-8
    high_school_content = Column(JSON, nullable=True)  # Grades 9-12
    advanced_content = Column(JSON, nullable=True)  # Advanced/AP level
    college_content = Column(JSON, nullable=True)  # Undergraduate/Graduate
    
    # Content example structure:
    # {
    #     "content": "Full lesson text...",
    #     "learning_objectives": ["Objective 1", "Objective 2"],
    #     "key_concepts": ["Concept 1", "Concept 2"],
    #     "activities": ["Activity 1", "Activity 2"],
    #     "assessment": "Assessment details...",
    #     "estimated_time_minutes": 45
    # }
    
    # Subject and Standards
    subjects = Column(JSON, nullable=False, default=list)  # e.g., ['Physics', 'Engineering']
    standards_aligned = Column(JSON, nullable=False, default=list)  # e.g., ['NGSS-HS-PS2-1']
    
    # Media Resources
    video_urls = Column(JSON, nullable=False, default=list)  # Array of video URLs
    # video_urls example: [
    #     {"title": "Introduction", "url": "https://..."},
    #     {"title": "Deep Dive", "url": "https://..."}
    # ]
    
    simulation_urls = Column(JSON, nullable=False, default=list)  # Interactive simulations
    # simulation_urls example: [
    #     {"title": "Physics Simulator", "url": "https://phet.colorado.edu/...", "type": "phet"}
    # ]
    
    # Career Connections
    career_paths = Column(JSON, nullable=False, default=list)  # Related careers
    # career_paths example: [
    #     {"title": "Physicist", "description": "...", "salary_range": "..."},
    #     {"title": "Engineer", "description": "...", "salary_range": "..."}
    # ]
    
    # Publication and Status
    status = Column(Enum(LessonStatus), nullable=False, default=LessonStatus.DRAFT, index=True)
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Engagement Metrics
    views_count = Column(Integer, default=0)
    completions_count = Column(Integer, default=0)
    avg_rating = Column(Float, nullable=True)  # 0.0 to 5.0
    
    # Metadata and Additional Info
    metadata = Column(JSON, nullable=False, default={})
    # metadata example:
    # {
    #     "difficulty_level": 3,  # 1-5 scale
    #     "reading_level": "8th grade",
    #     "duration_minutes": 60,
    #     "tags": ["AI", "machine-learning", "future-skills"],
    #     "ai_generated": true,
    #     "language": "en"
    # }
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_news_article_id', 'news_article_id'),
        Index('idx_status', 'status'),
        Index('idx_published_at_desc', 'published_at'),
        Index('idx_created_by', 'created_by'),
        Index('idx_status_published', 'status', 'published_at'),
    )
    
    # Relationships
    news_article = relationship("NewsArticle", foreign_keys=[news_article_id], lazy="select")
    creator = relationship("User", foreign_keys=[created_by], lazy="select")
    
    def __repr__(self) -> str:
        """String representation of Lesson"""
        return (
            f"<Lesson(id={self.id}, title={self.title[:50]}..., "
            f"status={self.status.value}, views={self.views_count})>"
        )
    
    def __str__(self) -> str:
        """User-friendly string representation"""
        return f"{self.title} ({self.status.value})"
    
    @property
    def is_published(self) -> bool:
        """Check if lesson is published"""
        return self.status == LessonStatus.PUBLISHED
    
    @property
    def is_draft(self) -> bool:
        """Check if lesson is in draft status"""
        return self.status == LessonStatus.DRAFT
    
    @property
    def is_archived(self) -> bool:
        """Check if lesson is archived"""
        return self.status == LessonStatus.ARCHIVED
    
    @property
    def has_video(self) -> bool:
        """Check if lesson has video resources"""
        return isinstance(self.video_urls, list) and len(self.video_urls) > 0
    
    @property
    def has_simulation(self) -> bool:
        """Check if lesson has interactive simulations"""
        return isinstance(self.simulation_urls, list) and len(self.simulation_urls) > 0
    
    @property
    def has_career_connections(self) -> bool:
        """Check if lesson has career path connections"""
        return isinstance(self.career_paths, list) and len(self.career_paths) > 0
    
    @property
    def completion_rate(self) -> float:
        """Calculate completion rate
        
        Returns:
            Completion rate as percentage (0-100)
        """
        if self.views_count == 0:
            return 0.0
        return (self.completions_count / self.views_count) * 100
    
    def get_content_for_level(self, level: str) -> dict:
        """Get content for a specific educational level
        
        Args:
            level: Educational level ('elementary', 'middle', 'high', 'advanced', 'college')
            
        Returns:
            Content dictionary for the level, or empty dict if not available
        """
        level_map = {
            'elementary': self.elementary_content,
            'middle': self.middle_school_content,
            'high': self.high_school_content,
            'advanced': self.advanced_content,
            'college': self.college_content,
        }
        content = level_map.get(level, {})
        return content if isinstance(content, dict) else {}
    
    def set_content_for_level(self, level: str, content: dict) -> None:
        """Set content for a specific educational level
        
        Args:
            level: Educational level
            content: Content dictionary
        """
        level_map = {
            'elementary': 'elementary_content',
            'middle': 'middle_school_content',
            'high': 'high_school_content',
            'advanced': 'advanced_content',
            'college': 'college_content',
        }
        if level in level_map:
            setattr(self, level_map[level], content)
    
    def add_subject(self, subject: str) -> None:
        """Add a subject to the lesson
        
        Args:
            subject: Subject name
        """
        if not isinstance(self.subjects, list):
            self.subjects = []
        if subject not in self.subjects:
            self.subjects.append(subject)
    
    def remove_subject(self, subject: str) -> None:
        """Remove a subject from the lesson
        
        Args:
            subject: Subject name
        """
        if isinstance(self.subjects, list) and subject in self.subjects:
            self.subjects.remove(subject)
    
    def add_standard(self, standard: str) -> None:
        """Add an educational standard
        
        Args:
            standard: Standard code (e.g., 'NGSS-HS-PS2-1')
        """
        if not isinstance(self.standards_aligned, list):
            self.standards_aligned = []
        if standard not in self.standards_aligned:
            self.standards_aligned.append(standard)
    
    def add_video(self, title: str, url: str) -> None:
        """Add a video resource
        
        Args:
            title: Video title
            url: Video URL
        """
        if not isinstance(self.video_urls, list):
            self.video_urls = []
        video = {"title": title, "url": url}
        if video not in self.video_urls:
            self.video_urls.append(video)
    
    def add_simulation(self, title: str, url: str, sim_type: str = "interactive") -> None:
        """Add a simulation resource
        
        Args:
            title: Simulation title
            url: Simulation URL
            sim_type: Type of simulation
        """
        if not isinstance(self.simulation_urls, list):
            self.simulation_urls = []
        simulation = {"title": title, "url": url, "type": sim_type}
        if simulation not in self.simulation_urls:
            self.simulation_urls.append(simulation)
    
    def add_career_path(self, title: str, description: str, salary_range: str = None) -> None:
        """Add a career path connection
        
        Args:
            title: Career title
            description: Career description
            salary_range: Estimated salary range
        """
        if not isinstance(self.career_paths, list):
            self.career_paths = []
        career = {
            "title": title,
            "description": description,
            "salary_range": salary_range
        }
        if career not in self.career_paths:
            self.career_paths.append(career)
    
    def increment_views(self, count: int = 1) -> None:
        """Increment view count
        
        Args:
            count: Number of views to add
        """
        self.views_count += count
    
    def increment_completions(self, count: int = 1) -> None:
        """Increment completion count
        
        Args:
            count: Number of completions to add
        """
        self.completions_count += count
    
    def set_rating(self, rating: float) -> None:
        """Set the average rating
        
        Args:
            rating: Rating value (0.0 to 5.0)
        """
        if 0.0 <= rating <= 5.0:
            self.avg_rating = rating
    
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
            default: Default value if not found
            
        Returns:
            Metadata value or default
        """
        if not isinstance(self.metadata, dict):
            return default
        return self.metadata.get(key, default)
    
    def to_dict(self, include_all_levels: bool = False) -> dict:
        """Convert lesson to dictionary
        
        Args:
            include_all_levels: Whether to include all content levels
            
        Returns:
            Dictionary representation of lesson
        """
        lesson_dict = {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "subjects": self.subjects,
            "standards_aligned": self.standards_aligned,
            "status": self.status.value,
            "news_article_id": self.news_article_id,
            "created_by": self.created_by,
            "video_urls": self.video_urls,
            "simulation_urls": self.simulation_urls,
            "career_paths": self.career_paths,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "views_count": self.views_count,
            "completions_count": self.completions_count,
            "completion_rate": self.completion_rate,
            "avg_rating": self.avg_rating,
            "has_video": self.has_video,
            "has_simulation": self.has_simulation,
            "has_career_connections": self.has_career_connections,
        }
        
        if include_all_levels:
            lesson_dict.update({
                "elementary_content": self.elementary_content,
                "middle_school_content": self.middle_school_content,
                "high_school_content": self.high_school_content,
                "advanced_content": self.advanced_content,
                "college_content": self.college_content,
            })
        
        if self.metadata:
            lesson_dict["metadata"] = self.metadata
        
        return lesson_dict

