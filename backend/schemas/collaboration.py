"""
Collaboration Response Schemas

Pydantic models for collaboration rooms, study groups, and shared simulations.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RoomMember(BaseModel):
    """Member in a collaboration room"""
    user_id: str
    username: str
    role: str = "member"  # host, member
    joined_at: datetime


class CollaborationRoomResponse(BaseModel):
    """Response representing a collaboration room"""
    id: str
    title: str
    description: Optional[str] = None
    lesson_id: Optional[str] = None
    is_private: bool = False
    max_members: int = 10
    current_members_count: int = 0
    members: List[RoomMember] = []
    created_by: str
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True


class RoomsListResponse(BaseModel):
    """Paginated list of collaboration rooms"""
    items: List[CollaborationRoomResponse]
    total: int


class CreateRoomRequest(BaseModel):
    """Request to create a new collaboration room"""
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    lesson_id: Optional[str] = None
    is_private: bool = False
    max_members: int = Field(10, ge=2, le=50)


class RoleUpdatePayload(BaseModel):
    """Payload for updating user role in a room"""
    role: str = Field(..., pattern="^(host|member)$")
