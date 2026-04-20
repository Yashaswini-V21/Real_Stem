"""Student learning progress model for RealSTEM"""
from sqlalchemy import (
    Column, String, DateTime, Integer, Float, Boolean, JSON, 
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timedelta
import uuid

Base = declarative_base()


class StudentProgress(Base):
    """StudentProgress model for tracking learning journey
    
    Tracks individual student progress through lessons including time spent,
    activities completed, assessments taken, concepts mastered, and collaborative work.
    """
    __tablename__ = "student_progress"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Relationships
    student_id = Column(
        String, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    lesson_id = Column(
        String, 
        ForeignKey("lessons.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Optional team/collaboration
    team_id = Column(Integer, nullable=True, index=True)  # For group projects
    
    # Learning Path Configuration
    difficulty_level = Column(
        String(50), 
        nullable=False, 
        default="middle_school",
        index=True
    )
    # Values: 'elementary', 'middle_school', 'high_school', 'advanced', 'college'
    
    # Progress Timeline
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Time Investment
    time_spent_seconds = Column(Integer, default=0)  # Total time spent
    
    # Learning Activities Completion
    video_watched = Column(Boolean, default=False)  # Video content viewed
    simulation_completed = Column(Boolean, default=False)  # Interactive simulation done
    
    # Activities Tracking
    activities_done = Column(JSON, nullable=False, default=list)
    # Format: [
    #     {"id": "activity_1", "name": "Lab 1", "completed": true, "score": 95},
    #     {"id": "activity_2", "name": "Discussion", "completed": false, "score": null}
    # ]
    
    # Assessment Results
    assessment_score = Column(Float, nullable=True)  # 0-100 score
    
    # Conceptual Learning Progress
    struggled_with = Column(JSON, nullable=False, default=list)  # Concepts student struggles with
    # Format: ["quantum mechanics", "wave-particle duality"]
    
    mastered_concepts = Column(JSON, nullable=False, default=list)  # Concepts student mastered
    # Format: ["photons", "energy levels"]
    
    # Collaborative Learning
    contributions = Column(JSON, nullable=True)  # Group project contributions
    # Format: {
    #     "notes": "Worked on part 1 and 2",
    #     "files_submitted": ["experiment_1.pdf", "analysis.xlsx"],
    #     "collaboration_score": 90
    # }
    
    # Flexible Metadata
    metadata = Column(JSON, nullable=False, default={})
    # Format: {
    #     "preferred_learning_style": "visual",
    #     "adaptive_adjustments": ["increased_time_limits", "more_examples"],
    #     "learning_pace": "slower",
    #     "ai_recommendations": ["review_videos", "try_simulation"],
    #     "parent_notifications_sent": 2
    # }
    
    # Engagement Metrics
    attempts = Column(Integer, default=1)  # Number of attempts at this lesson
    help_requests = Column(Integer, default=0)  # Number of times student asked for help
    
    # System Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite constraints and indexes
    __table_args__ = (
        UniqueConstraint('student_id', 'lesson_id', name='uq_student_lesson'),
        Index('idx_student_id', 'student_id'),
        Index('idx_lesson_id', 'lesson_id'),
        Index('idx_team_id', 'team_id'),
        Index('idx_started_at', 'started_at'),
        Index('idx_completed_at', 'completed_at'),
        Index('idx_student_lesson_team', 'student_id', 'lesson_id', 'team_id'),
    )
    
    # Relationships
    student = relationship("User", foreign_keys=[student_id], lazy="select")
    lesson = relationship("Lesson", foreign_keys=[lesson_id], lazy="select")
    
    def __repr__(self) -> str:
        """String representation of StudentProgress"""
        return (
            f"<StudentProgress(student_id={self.student_id}, lesson_id={self.lesson_id}, "
            f"level={self.difficulty_level}, completed={self.is_completed})>"
        )
    
    def __str__(self) -> str:
        """User-friendly string representation"""
        status = "Completed" if self.is_completed else "In Progress"
        return f"Progress: {self.student_id} - {self.lesson_id} ({status})"
    
    @property
    def is_completed(self) -> bool:
        """Check if lesson is completed
        
        Returns:
            True if lesson has been completed
        """
        return self.completed_at is not None
    
    @property
    def completion_percentage(self) -> float:
        """Calculate lesson completion percentage
        
        Returns:
            Completion percentage (0-100)
        """
        if self.is_completed:
            return 100.0
        
        # Calculate based on activities completed
        if not isinstance(self.activities_done, list) or len(self.activities_done) == 0:
            return 0.0
        
        completed = sum(1 for activity in self.activities_done if activity.get('completed', False))
        return (completed / len(self.activities_done)) * 100
    
    @property
    def total_time_spent(self) -> timedelta:
        """Get total time spent as timedelta
        
        Returns:
            Timedelta object
        """
        return timedelta(seconds=self.time_spent_seconds)
    
    @property
    def total_time_formatted(self) -> str:
        """Get formatted time spent
        
        Returns:
            Formatted string like "1h 30m 45s"
        """
        hours, remainder = divmod(self.time_spent_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    @property
    def days_in_progress(self) -> int:
        """Calculate days lesson has been in progress
        
        Returns:
            Number of days
        """
        end_time = self.completed_at or datetime.utcnow()
        delta = end_time - self.started_at
        return delta.days
    
    @property
    def activities_completion_rate(self) -> float:
        """Calculate activity completion rate
        
        Returns:
            Percentage of activities completed (0-100)
        """
        if not isinstance(self.activities_done, list) or len(self.activities_done) == 0:
            return 0.0
        
        completed = sum(1 for activity in self.activities_done if activity.get('completed', False))
        return (completed / len(self.activities_done)) * 100
    
    @property
    def concept_mastery_count(self) -> int:
        """Count of mastered concepts
        
        Returns:
            Number of mastered concepts
        """
        return len(self.mastered_concepts) if isinstance(self.mastered_concepts, list) else 0
    
    @property
    def concepts_struggling_count(self) -> int:
        """Count of concepts student struggles with
        
        Returns:
            Number of struggled concepts
        """
        return len(self.struggled_with) if isinstance(self.struggled_with, list) else 0
    
    def start_lesson(self) -> None:
        """Mark lesson as started"""
        self.started_at = datetime.utcnow()
        self.last_accessed_at = datetime.utcnow()
    
    def complete_lesson(self, score: float = None) -> None:
        """Mark lesson as completed
        
        Args:
            score: Optional assessment score (0-100)
        """
        self.completed_at = datetime.utcnow()
        if score is not None and 0 <= score <= 100:
            self.assessment_score = score
    
    def add_time(self, seconds: int) -> None:
        """Add time to total time spent
        
        Args:
            seconds: Number of seconds to add
        """
        self.time_spent_seconds += seconds
        self.last_accessed_at = datetime.utcnow()
    
    def mark_video_watched(self) -> None:
        """Mark video as watched"""
        self.video_watched = True
        self.last_accessed_at = datetime.utcnow()
    
    def mark_simulation_completed(self) -> None:
        """Mark simulation as completed"""
        self.simulation_completed = True
        self.last_accessed_at = datetime.utcnow()
    
    def complete_activity(self, activity_id: str, score: float = None) -> None:
        """Mark an activity as completed
        
        Args:
            activity_id: ID of the activity
            score: Optional score for the activity (0-100)
        """
        if not isinstance(self.activities_done, list):
            self.activities_done = []
        
        # Find or create activity entry
        for activity in self.activities_done:
            if activity.get('id') == activity_id:
                activity['completed'] = True
                if score is not None:
                    activity['score'] = score
                break
        else:
            # Activity not found, create new entry
            self.activities_done.append({
                'id': activity_id,
                'completed': True,
                'score': score
            })
    
    def add_struggled_concept(self, concept: str) -> None:
        """Add a concept the student struggles with
        
        Args:
            concept: Concept name
        """
        if not isinstance(self.struggled_with, list):
            self.struggled_with = []
        if concept not in self.struggled_with:
            self.struggled_with.append(concept)
            # Remove from mastered if present
            if isinstance(self.mastered_concepts, list) and concept in self.mastered_concepts:
                self.mastered_concepts.remove(concept)
    
    def add_mastered_concept(self, concept: str) -> None:
        """Mark a concept as mastered
        
        Args:
            concept: Concept name
        """
        if not isinstance(self.mastered_concepts, list):
            self.mastered_concepts = []
        if concept not in self.mastered_concepts:
            self.mastered_concepts.append(concept)
            # Remove from struggled if present
            if isinstance(self.struggled_with, list) and concept in self.struggled_with:
                self.struggled_with.remove(concept)
    
    def set_difficulty_level(self, level: str) -> None:
        """Update difficulty level (adaptive learning)
        
        Args:
            level: One of 'elementary', 'middle_school', 'high_school', 'advanced', 'college'
        """
        valid_levels = ['elementary', 'middle_school', 'high_school', 'advanced', 'college']
        if level in valid_levels:
            self.difficulty_level = level
    
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
    
    def set_contribution_notes(self, notes: str) -> None:
        """Set collaboration contribution notes
        
        Args:
            notes: Contribution notes
        """
        if not isinstance(self.contributions, dict):
            self.contributions = {}
        self.contributions['notes'] = notes
    
    def increment_help_requests(self) -> None:
        """Increment help request counter"""
        self.help_requests += 1
    
    def increment_attempts(self) -> None:
        """Increment lesson attempt counter"""
        self.attempts += 1
    
    def to_dict(self, include_relationships: bool = False) -> dict:
        """Convert progress to dictionary
        
        Args:
            include_relationships: Whether to include related objects
            
        Returns:
            Dictionary representation of progress
        """
        progress_dict = {
            "id": self.id,
            "student_id": self.student_id,
            "lesson_id": self.lesson_id,
            "team_id": self.team_id,
            "difficulty_level": self.difficulty_level,
            "is_completed": self.is_completed,
            "completion_percentage": self.completion_percentage,
            "activities_completion_rate": self.activities_completion_rate,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "time_spent_seconds": self.time_spent_seconds,
            "time_spent_formatted": self.total_time_formatted,
            "days_in_progress": self.days_in_progress,
            "video_watched": self.video_watched,
            "simulation_completed": self.simulation_completed,
            "activities_done": self.activities_done,
            "assessment_score": self.assessment_score,
            "mastered_concepts": self.mastered_concepts,
            "mastered_concepts_count": self.concept_mastery_count,
            "struggled_with": self.struggled_with,
            "struggled_concepts_count": self.concepts_struggling_count,
            "attempts": self.attempts,
            "help_requests": self.help_requests,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if self.contributions:
            progress_dict["contributions"] = self.contributions
        
        if self.metadata:
            progress_dict["metadata"] = self.metadata
        
        if include_relationships:
            if self.student:
                progress_dict["student"] = {
                    "id": self.student.id,
                    "name": self.student.name,
                    "email": self.student.email,
                }
            if self.lesson:
                progress_dict["lesson"] = {
                    "id": self.lesson.id,
                    "title": self.lesson.title,
                }
        
        return progress_dict

