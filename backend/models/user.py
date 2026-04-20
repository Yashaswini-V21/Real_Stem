"""User model for RealSTEM authentication and profile management"""
from sqlalchemy import Column, String, DateTime, Boolean, Enum, JSON, Index, LargeBinary
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class UserRole(str, enum.Enum):
    """User role enumeration"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    """User model for RealSTEM platform
    
    Represents a user account with authentication, profile information,
    and learning preferences.
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(LargeBinary, nullable=False)
    
    # User Information
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=True, default="Unknown")
    language = Column(String(5), nullable=False, default="en", index=True)
    
    # Role and Permissions
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT, index=True)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    is_email_verified = Column(Boolean, default=False)
    
    # Learning Profile (Student-specific)
    grade_level = Column(String(50), nullable=True)  # e.g., "Grade 9", "Undergraduate"
    
    # Teaching Profile (Teacher-specific)
    # Stored as JSON array of subject names
    subjects = Column(JSON, nullable=True, default=list)  # e.g., ["Physics", "Chemistry"]
    
    # User Preferences and Settings
    preferences = Column(JSON, nullable=False, default={
        "theme": "light",
        "notifications_enabled": True,
        "email_updates": True,
        "show_progress": True,
        "difficulty_level": "adaptive"
    })
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    # Metadata
    bio = Column(String(500), nullable=True)  # User bio/description
    avatar_url = Column(String(500), nullable=True)  # Profile picture URL
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_email_active', 'email', 'is_active'),
        Index('idx_role_active', 'role', 'is_active'),
        Index('idx_language_active', 'language', 'is_active'),
        Index('idx_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        """String representation of User"""
        return (
            f"<User(id={self.id}, email={self.email}, name={self.name}, "
            f"role={self.role.value}, active={self.is_active})>"
        )
    
    def __str__(self) -> str:
        """User display string"""
        return f"{self.name} ({self.email})"
    
    @property
    def is_student(self) -> bool:
        """Check if user is a student"""
        return self.role == UserRole.STUDENT
    
    @property
    def is_teacher(self) -> bool:
        """Check if user is a teacher"""
        return self.role == UserRole.TEACHER
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.role == UserRole.ADMIN
    
    @property
    def display_name(self) -> str:
        """Get user's display name"""
        return self.name or self.email.split('@')[0]
    
    def set_preference(self, key: str, value) -> None:
        """Set a user preference
        
        Args:
            key: Preference key
            value: Preference value
        """
        if not isinstance(self.preferences, dict):
            self.preferences = {}
        self.preferences[key] = value
    
    def get_preference(self, key: str, default=None):
        """Get a user preference
        
        Args:
            key: Preference key
            default: Default value if key not found
            
        Returns:
            Preference value or default
        """
        if not isinstance(self.preferences, dict):
            return default
        return self.preferences.get(key, default)
    
    def add_subject(self, subject: str) -> None:
        """Add a subject (for teachers)
        
        Args:
            subject: Subject name to add
        """
        if not isinstance(self.subjects, list):
            self.subjects = []
        if subject not in self.subjects:
            self.subjects.append(subject)
    
    def remove_subject(self, subject: str) -> None:
        """Remove a subject (for teachers)
        
        Args:
            subject: Subject name to remove
        """
        if isinstance(self.subjects, list) and subject in self.subjects:
            self.subjects.remove(subject)
    
    def has_subject(self, subject: str) -> bool:
        """Check if teacher has a specific subject
        
        Args:
            subject: Subject name to check
            
        Returns:
            True if teacher has the subject, False otherwise
        """
        if not isinstance(self.subjects, list):
            return False
        return subject in self.subjects
    
    def to_dict(self, include_password: bool = False) -> dict:
        """Convert user to dictionary
        
        Args:
            include_password: Whether to include password_hash in output
            
        Returns:
            Dictionary representation of user
        """
        user_dict = {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "country": self.country,
            "language": self.language,
            "role": self.role.value,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_email_verified": self.is_email_verified,
            "grade_level": self.grade_level,
            "subjects": self.subjects,
            "preferences": self.preferences,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
        }
        
        if include_password:
            user_dict["password_hash"] = self.password_hash
        
        return user_dict

