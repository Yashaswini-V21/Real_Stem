"""
Collaboration Models for RealSTEM

Defines models for study rooms, shared simulations, and real-time interaction metadata.
"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class CollaborationRoom(Base):
    """Study room for students to collaborate on lessons or simulations"""
    __tablename__ = "collaboration_rooms"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Linked Lesson (Optional)
    lesson_id = Column(String, ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True)
    
    # Settings
    is_private = Column(Boolean, default=False)
    room_code = Column(String(10), unique=True, nullable=True)  # For private rooms
    max_members = Column(Integer, default=10)
    
    # Ownership
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # State
    is_active = Column(Boolean, default=True)
    shared_state = Column(JSON, default=dict)  # Stores simulation state, canvas data, etc.

    # Relationships
    members = relationship("RoomMember", back_populates="room", cascade="all, delete-orphan")
    lesson = relationship("Lesson", lazy="select")

class RoomMember(Base):
    """Association table with extra data for room membership"""
    __tablename__ = "room_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String, ForeignKey("collaboration_rooms.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    role = Column(String(20), default="member")  # host, speaker, listener
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_present = Column(Boolean, default=True)  # Current presence status

    # Relationships
    room = relationship("CollaborationRoom", back_populates="members")
    user = relationship("User", lazy="select")
