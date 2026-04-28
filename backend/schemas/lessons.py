"""
Lesson Response Schemas

Pydantic models for lesson API responses with proper serialization and documentation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LessonContentResponse(BaseModel):
    """Content for a specific difficulty level"""
    
    id: str = Field(..., description="Content ID")
    lesson_id: str = Field(..., description="Parent lesson ID")
    difficulty_level: str = Field(..., description="Difficulty level")
    learning_objectives: List[str] = Field(default=[], description="Learning objectives")
    content: str = Field(..., description="Main lesson content")
    activities: List[Dict[str, Any]] = Field(default=[], description="Learning activities")
    materials: List[Dict[str, Any]] = Field(default=[], description="Required materials")
    keywords: List[str] = Field(default=[], description="Key concepts and keywords")
    estimated_time_minutes: int = Field(default=45, description="Estimated time to complete")
    
    class Config:
        from_attributes = True


class LessonResponse(BaseModel):
    """Lesson in list response"""
    
    id: str = Field(..., description="Unique lesson ID")
    title: str = Field(..., description="Lesson title")
    summary: Optional[str] = Field(None, description="Lesson summary")
    status: str = Field(..., description="Lesson status (draft, published, archived)")
    difficulty_levels: List[str] = Field(..., description="Supported difficulty levels")
    subjects: List[str] = Field(..., description="STEM subjects covered")
    source_article_id: Optional[str] = Field(None, description="ID of source news article")
    views_count: int = Field(default=0, description="Number of times lesson was viewed")
    avg_rating: Optional[float] = Field(None, ge=0, le=5, description="Average user rating")
    rating_count: int = Field(default=0, description="Number of ratings")
    created_at: datetime = Field(..., description="When lesson was created")
    published_at: Optional[datetime] = Field(None, description="When lesson was published")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "lesson_123",
                "title": "Quantum Computing Fundamentals",
                "summary": "An introduction to quantum computing concepts",
                "status": "published",
                "difficulty_levels": ["high_school", "advanced", "college"],
                "subjects": ["physics", "computer_science", "technology"],
                "source_article_id": "news_456",
                "views_count": 1500,
                "avg_rating": 4.8,
                "rating_count": 245,
                "created_at": "2026-04-22T10:00:00Z",
                "published_at": "2026-04-22T11:00:00Z",
            }
        }


class LessonDetailResponse(LessonResponse):
    """Detailed lesson response with full content and metadata"""
    
    standards_aligned: List[str] = Field(default=[], description="Educational standards aligned")
    career_paths: List[Dict[str, Any]] = Field(default=[], description="Related career paths")
    key_concepts: List[str] = Field(default=[], description="Key concepts covered")
    prerequisite_lessons: List[str] = Field(default=[], description="IDs of prerequisite lessons")
    follow_up_lessons: List[str] = Field(default=[], description="IDs of follow-up lessons")
    video_urls: List[str] = Field(default=[], description="URLs to educational videos")
    simulation_urls: List[str] = Field(default=[], description="URLs to interactive simulations")
    difficulty_content: Dict[str, LessonContentResponse] = Field(
        default={}, description="Content for each difficulty level"
    )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "lesson_123",
                "title": "Quantum Computing Fundamentals",
                "standards_aligned": ["NGSS-PS4-3", "ISTE-3b"],
                "career_paths": [
                    {"career": "Quantum Engineer", "company": "IBM"},
                    {"career": "Research Physicist", "company": "Academia"}
                ],
                "key_concepts": ["superposition", "entanglement", "quantum gates"],
                "video_urls": ["/api/media/videos/lesson_123_high_school.mp4"],
                "simulation_urls": ["/api/media/simulations/lesson_123_physics_20260422.html"],
            }
        }


class LessonsListResponse(BaseModel):
    """Paginated list of lessons"""
    
    items: List[LessonResponse] = Field(..., description="Array of lessons")
    total: int = Field(..., ge=0, description="Total number of lessons matching query")
    limit: int = Field(..., ge=1, description="Number of items per page")
    offset: int = Field(..., ge=0, description="Number of items skipped")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": "lesson_123",
                        "title": "Quantum Computing",
                        "status": "published",
                        "difficulty_levels": ["high_school", "college"],
                    }
                ],
                "total": 150,
                "limit": 50,
                "offset": 0,
            }
        }


class GenerateLessonRequest(BaseModel):
    """Request to generate a lesson from a news article"""
    
    news_article_id: str = Field(..., description="ID of news article to base lesson on")
    breaking_news_mode: bool = Field(
        default=False,
        description="Use breaking news mode for urgent/trending topics"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "news_article_id": "news_123",
                "breaking_news_mode": True,
            }
        }


class GenerateLessonResponse(BaseModel):
    """Response from lesson generation"""
    
    lesson_id: str = Field(..., description="ID of generated lesson")
    title: str = Field(..., description="Lesson title")
    status: str = Field(..., description="Initial status (always 'draft')")
    difficulty_levels: List[str] = Field(..., description="Supported levels")
    subjects: List[str] = Field(..., description="STEM subjects covered")
    created_at: datetime = Field(..., description="When lesson was created")
    message: str = Field(..., description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lesson_id": "lesson_123",
                "title": "AI Breakthrough in Medical Imaging",
                "status": "draft",
                "difficulty_levels": ["middle_school", "high_school", "college"],
                "subjects": ["computer_science", "technology", "engineering"],
                "created_at": "2026-04-22T12:00:00Z",
                "message": "Lesson generated successfully"
            }
        }


class PublishLessonResponse(BaseModel):
    """Response from publishing a lesson"""
    
    lesson_id: str = Field(..., description="ID of published lesson")
    title: str = Field(..., description="Lesson title")
    status: str = Field(..., description="New status (always 'published')")
    published_at: datetime = Field(..., description="Publication timestamp")
    message: str = Field(..., description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lesson_id": "lesson_123",
                "title": "AI Breakthrough in Medical Imaging",
                "status": "published",
                "published_at": "2026-04-22T12:15:00Z",
                "message": "Lesson published successfully"
            }
        }


class RateLessonRequest(BaseModel):
    """Request to rate a lesson"""
    
    rating: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Rating from 1.0 (poor) to 5.0 (excellent)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "rating": 4.5
            }
        }


class LessonStatsResponse(BaseModel):
    """Statistics about lessons in the system"""
    
    total_lessons: int = Field(..., description="Total lessons in database")
    published_lessons: int = Field(..., description="Published lessons")
    draft_lessons: int = Field(..., description="Draft lessons awaiting publication")
    avg_rating: float = Field(..., ge=0, le=5, description="Average rating across all lessons")
    total_views: int = Field(..., description="Total lesson views")
    most_viewed: List[str] = Field(..., description="IDs of most viewed lessons")
    most_rated: List[str] = Field(..., description="IDs of highest rated lessons")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_lessons": 500,
                "published_lessons": 450,
                "draft_lessons": 50,
                "avg_rating": 4.6,
                "total_views": 150000,
                "most_viewed": ["lesson_123", "lesson_456"],
                "most_rated": ["lesson_789", "lesson_101"],
            }
        }


class LessonFilterParams(BaseModel):
    """Parameters for filtering lessons"""
    
    status: str = Field(default="published", description="Lesson status")
    difficulty_level: Optional[str] = Field(None, description="Filter by difficulty level")
    subjects: Optional[List[str]] = Field(None, description="Filter by STEM subjects")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum average rating")
    has_video: bool = Field(default=False, description="Only lessons with videos")
    has_simulation: bool = Field(default=False, description="Only lessons with simulations")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "published",
                "difficulty_level": "high_school",
                "subjects": ["physics", "mathematics"],
                "min_rating": 4.0,
                "has_video": True,
            }
        }
