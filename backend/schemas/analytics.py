"""
Analytics Response Schemas

Pydantic models for student performance, lesson engagement, and knowledge gap analysis.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StudentProgressResponse(BaseModel):
    """Overall progress for a specific student"""
    user_id: str
    lessons_completed: int = 0
    lessons_in_progress: int = 0
    total_time_spent_minutes: int = 0
    average_score: float = 0.0
    subjects_mastery: Dict[str, float] = {}  # e.g. {"physics": 0.85, "math": 0.70}
    last_active_at: Optional[datetime] = None


class LessonEngagementResponse(BaseModel):
    """Engagement metrics for a specific lesson"""
    lesson_id: str
    total_views: int
    completion_rate: float
    average_time_spent: int
    average_rating: float
    feedback_summary: List[str] = []


class SubjectTrendsResponse(BaseModel):
    """Trending STEM subjects based on student interest and scores"""
    subject: str
    growth_rate: float
    average_score: float
    student_count: int


class AssessmentMetric(BaseModel):
    """Data for a single assessment question/topic"""
    topic: str
    difficulty: str
    success_rate: float
    average_time_seconds: int


class KnowledgeGapResponse(BaseModel):
    """Identified learning gaps for a student"""
    student_id: str
    subject: str
    identified_gaps: List[str]
    recommended_lessons: List[str]
    confidence_level: float
