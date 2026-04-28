"""
Collaboration API Endpoints

Provides router for study rooms, shared simulations, and real-time collaboration session management.
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from database import get_db
from utils.logger import get_logger
from utils.auth import get_current_user

# Models and Schemas
from models.collaboration import CollaborationRoom, RoomMember
from models.lesson import Lesson
from schemas.collaboration import (
    CollaborationRoomResponse,
    RoomsListResponse,
    CreateRoomRequest,
    RoleUpdatePayload,
    RoomMember as RoomMemberSchema
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/collaboration", tags=["collaboration"])

@router.get("/rooms", response_model=RoomsListResponse)
async def get_rooms(
    lesson_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get active public collaboration rooms with optional lesson filtering"""
    query = db.query(CollaborationRoom).filter(CollaborationRoom.is_private == False)
    
    if lesson_id:
        query = query.filter(CollaborationRoom.lesson_id == lesson_id)
        
    total = query.count()
    rooms = query.order_by(desc(CollaborationRoom.last_active)).offset(offset).limit(limit).all()
    
    return {
        "items": rooms,
        "total": total
    }

@router.post("/rooms", response_model=CollaborationRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_in: CreateRoomRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new study room and join as host"""
    new_room = CollaborationRoom(
        title=room_in.title,
        description=room_in.description,
        lesson_id=room_in.lesson_id,
        is_private=room_in.is_private,
        max_members=room_in.max_members,
        created_by=current_user["id"]
    )
    
    db.add(new_room)
    db.flush() # Get ID
    
    # Add creator as host member
    host_member = RoomMember(
        room_id=new_room.id,
        user_id=current_user["id"],
        role="host"
    )
    db.add(host_member)
    db.commit()
    db.refresh(new_room)
    
    return new_room

@router.get("/rooms/{room_id}", response_model=CollaborationRoomResponse)
async def get_room_details(room_id: str, db: Session = Depends(get_db)):
    """Get details of a specific collaboration room"""
    room = db.query(CollaborationRoom).filter(CollaborationRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.post("/rooms/{room_id}/join")
async def join_room(
    room_id: str, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Join an existing collaboration room"""
    room = db.query(CollaborationRoom).filter(CollaborationRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if already a member
    existing = db.query(RoomMember).filter(
        and_(RoomMember.room_id == room_id, RoomMember.user_id == current_user["id"])
    ).first()
    
    if existing:
        existing.is_present = True
        db.commit()
        return {"message": "Rejoined room", "room_id": room_id}
    
    # Check capacity
    count = db.query(RoomMember).filter(RoomMember.room_id == room_id).count()
    if count >= room.max_members:
        raise HTTPException(status_code=400, detail="Room is full")
        
    new_member = RoomMember(
        room_id=room_id,
        user_id=current_user["id"],
        role="member"
    )
    db.add(new_member)
    db.commit()
    
    return {"message": "Joined room", "room_id": room_id}

@router.delete("/rooms/{room_id}/leave")
async def leave_room(
    room_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Leave a collaboration room"""
    member = db.query(RoomMember).filter(
        and_(RoomMember.room_id == room_id, RoomMember.user_id == current_user["id"])
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Not a member of this room")
        
    db.delete(member)
    db.commit()
    
    return {"message": "Left room"}

@router.patch("/rooms/{room_id}/state")
async def update_room_state(
    room_id: str,
    state_update: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update shared simulation state for all members"""
    room = db.query(CollaborationRoom).filter(CollaborationRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Simple JSON merge/update
    current_state = room.shared_state or {}
    current_state.update(state_update)
    room.shared_state = current_state
    room.last_active = datetime.utcnow()
    
    db.commit()
    return {"message": "State updated", "state": room.shared_state}

