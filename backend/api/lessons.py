"""
Lessons API Endpoints

Provides endpoints for fetching, filtering, generating, and managing educational lessons.
Integrates with AI generator for creating lessons from news articles.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, HTTPException, Depends, Query, Body, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from config import settings
from utils.logger import get_logger
from database import get_db
from models.lesson import Lesson, LessonStatus
from models.news import NewsArticle
from services.ai_generator import ai_generator
from schemas.lessons import (
    LessonResponse,
    LessonDetailResponse,
    LessonContentResponse,
    LessonsListResponse,
    GenerateLessonRequest,
    GenerateLessonResponse,
    RateLessonRequest,
    PublishLessonResponse,
)

from utils.auth import get_current_user, RoleChecker

logger = get_logger(__name__)

router = APIRouter(prefix="/api/lessons", tags=["lessons"])

# Role-based access
teacher_required = RoleChecker(["admin", "teacher"])
student_required = RoleChecker(["admin", "student"])


# Valid difficulty levels
VALID_LEVELS = ["elementary", "middle_school", "high_school", "advanced", "college"]
VALID_STATUSES = ["draft", "published", "archived"]
VALID_SUBJECTS = [
    "physics", "chemistry", "biology", "mathematics",
    "computer_science", "engineering", "astronomy", "geology",
    "environmental_science", "technology", "robotics", "data_science"
]


@router.get(
    "",
    response_model=LessonsListResponse,
    summary="Get lessons",
    description="Retrieve paginated list of lessons with filtering options",
)
async def get_lessons(
    status: str = Query("published", description="Lesson status filter"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    subject: Optional[str] = Query(None, description="Filter by STEM subject"),
    limit: int = Query(50, ge=1, le=500, description="Number of lessons to return"),
    offset: int = Query(0, ge=0, description="Number of lessons to skip"),
    db: Session = Depends(get_db),
) -> LessonsListResponse:
    """
    Get paginated list of lessons with optional filtering.
    """
    logger.info(
        f"📚 Fetching lessons: status={status}, level={difficulty_level}, "
        f"subject={subject}, limit={limit}, offset={offset}"
    )
    
    try:
        query = db.query(Lesson)
        
        # Filter by status
        if status in VALID_STATUSES:
            query = query.filter(Lesson.status == status)
        
        # Filter by difficulty level
        if difficulty_level and difficulty_level in VALID_LEVELS:
            # Check for content existence in specific JSON columns
            if difficulty_level == "elementary":
                query = query.filter(Lesson.elementary_content != None)
            elif difficulty_level == "middle_school":
                query = query.filter(Lesson.middle_school_content != None)
            elif difficulty_level == "high_school":
                query = query.filter(Lesson.high_school_content != None)
            elif difficulty_level == "advanced":
                query = query.filter(Lesson.advanced_content != None)
            elif difficulty_level == "college":
                query = query.filter(Lesson.college_content != None)
        
        # Filter by subject
        if subject and subject in VALID_SUBJECTS:
            query = query.filter(Lesson.subjects.contains(subject))
        
        # Get total count
        total = query.count()
        
        # Apply ordering and pagination
        lessons = (
            query.order_by(desc(Lesson.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        logger.info(f"✅ Retrieved {len(lessons)} lessons (total: {total})")
        
        items = []
        for l in lessons:
            items.append(
                LessonResponse(
                    id=l.id,
                    title=l.title,
                    summary=l.summary,
                    status=l.status.value,
                    difficulty_levels=[lv for lv in VALID_LEVELS if getattr(l, f"{lv}_content") is not None],
                    subjects=l.subjects,
                    source_article_id=l.news_article_id,
                    views_count=l.views_count,
                    avg_rating=l.avg_rating,
                    rating_count=getattr(l, 'rating_count', 0),
                    created_at=l.created_at,
                    published_at=l.published_at
                )
            )

        return LessonsListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
    
    except Exception as e:
        logger.error(f"❌ Error fetching lessons: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch lessons")


@router.get(
    "/{lesson_id}",
    response_model=LessonDetailResponse,
    summary="Get lesson detail",
    description="Retrieve a single lesson with all difficulty levels",
    responses={404: {"description": "Lesson not found"}},
)
async def get_lesson_detail(
    lesson_id: str,
    db: Session = Depends(get_db),
) -> LessonDetailResponse:
    """
    Get detailed information about a specific lesson.
    
    Path Parameters:
    - lesson_id: Unique identifier of the lesson
    """
    logger.info(f"📚 Fetching lesson detail: {lesson_id}")
    
    try:
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        
        if not lesson:
            logger.warning(f"⚠️ Lesson not found: {lesson_id}")
            raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} not found")
        
        # Increment view count
        lesson.views_count = (lesson.views_count or 0) + 1
        db.commit()
        db.refresh(lesson)
        
        # Build difficulty content map for the schema
        content_map = {}
        for level in VALID_LEVELS:
            content = getattr(lesson, f"{level}_content")
            if content:
                content["id"] = f"{lesson_id}_{level}"
                content["lesson_id"] = lesson_id
                content["difficulty_level"] = level
                content_map[level] = LessonContentResponse(**content)
        
        logger.info(f"✅ Retrieved lesson: {lesson.title[:50]}... (views: {lesson.views_count})")
        
        # Convert to response dict to handle JSON fields
        response_data = {
            "id": lesson.id,
            "title": lesson.title,
            "summary": lesson.summary,
            "status": lesson.status.value,
            "difficulty_levels": [l for l in VALID_LEVELS if getattr(lesson, f"{l}_content") is not None],
            "subjects": lesson.subjects,
            "source_article_id": lesson.news_article_id,
            "views_count": lesson.views_count,
            "avg_rating": lesson.avg_rating,
            "rating_count": getattr(lesson, 'rating_count', 0),
            "created_at": lesson.created_at,
            "published_at": lesson.published_at,
            "standards_aligned": lesson.standards_aligned,
            "career_paths": lesson.career_paths,
            "key_concepts": [], # Extracted from level-specific content if needed
            "video_urls": lesson.video_urls,
            "simulation_urls": lesson.simulation_urls,
            "difficulty_content": content_map
        }
        
        return LessonDetailResponse(**response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching lesson detail: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch lesson detail")


@router.get(
    "/{lesson_id}/content/{level}",
    response_model=LessonContentResponse,
    summary="Get lesson content for specific level",
    description="Retrieve content for a specific difficulty level",
    responses={
        404: {"description": "Lesson or level not found"},
        400: {"description": "Invalid difficulty level"},
    },
)
async def get_lesson_content(
    lesson_id: str,
    level: str,
    db: Session = Depends(get_db),
) -> LessonContentResponse:
    """
    Get lesson content for a specific difficulty level.
    
    Path Parameters:
    - lesson_id: Unique identifier of the lesson
    - level: Difficulty level (elementary, middle_school, high_school, advanced, college)
    
    Returns:
    - Content for the specified level only
    """
    logger.info(f"📚 Fetching lesson content: {lesson_id} / {level}")
    
    try:
        # Validate level
        if level not in VALID_LEVELS:
            logger.warning(f"⚠️ Invalid difficulty level: {level}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid level. Must be one of: {', '.join(VALID_LEVELS)}"
            )
        
        # Fetch lesson
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} not found")
        
        # In this model, content is stored in JSON columns on the Lesson model itself
        content_map = {
            "elementary": lesson.elementary_content,
            "middle_school": lesson.middle_school_content,
            "high_school": lesson.high_school_content,
            "advanced": lesson.advanced_content,
            "college": lesson.college_content
        }
        
        content = content_map.get(level)
        
        if not content:
            logger.warning(f"⚠️ Content not found for level: {level}")
            raise HTTPException(
                status_code=404,
                detail=f"Content not found for level: {level}"
            )
        
        logger.info(f"✅ Retrieved content for level: {level}")
        
        # Ensure ID and lesson_id are present for schema validation
        if isinstance(content, dict):
            content["id"] = f"{lesson_id}_{level}"
            content["lesson_id"] = lesson_id
            content["difficulty_level"] = level
            
        return LessonContentResponse(**content)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching lesson content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch lesson content")


@router.post(
    "/generate",
    response_model=GenerateLessonResponse,
    summary="Generate AI lesson",
    description="Generate a new lesson from a news article using AI",
    responses={
        400: {"description": "Invalid request"},
        403: {"description": "Not authorized (admin/teacher only)"},
        404: {"description": "News article not found"},
    },
)
async def generate_lesson(
    request: GenerateLessonRequest = Body(..., description="Lesson generation request"),
    current_user = Depends(teacher_required),
    db: Session = Depends(get_db),
) -> GenerateLessonResponse:
    """
    Generate a complete lesson from a news article using AI.
    """
    logger.info(
        f"🤖 Generating lesson from article: {request.news_article_id}, "
        f"breaking_news_mode={request.breaking_news_mode}"
    )
    
    try:
        # TODO: Add role-based authorization
        # if current_user["role"] not in ["admin", "teacher"]:
        #     raise HTTPException(status_code=403, detail="Not authorized")
        
        # Fetch the news article
        article = (
            db.query(NewsArticle)
            .filter(NewsArticle.id == request.news_article_id)
            .first()
        )
        
        if not article:
            logger.warning(f"⚠️ News article not found: {request.news_article_id}")
            raise HTTPException(
                status_code=404,
                detail=f"News article {request.news_article_id} not found"
            )
        
        logger.info(f"📰 Found article: {article.title[:50]}...")
        
        # Call AI generator
        logger.info("🔄 Calling AI lesson generator...")
        lesson = await ai_generator.generate_complete_lesson(
            article,
            user_id="user_123", # Assuming current user
            use_breaking_news_mode=request.breaking_news_mode
        )
        
        if not lesson:
            logger.error("❌ AI lesson generation failed")
            raise HTTPException(status_code=500, detail="Failed to generate lesson")
        
        # Save to database
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        
        logger.info(f"✅ Lesson generated and saved: {lesson.id}")
        
        return GenerateLessonResponse(
            lesson_id=lesson.id,
            title=lesson.title,
            status=lesson.status.value,
            difficulty_levels=[l for l in VALID_LEVELS if getattr(lesson, f"{l}_content") is not None],
            subjects=lesson.subjects,
            created_at=lesson.created_at,
            message="Lesson generated successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating lesson: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate lesson")


@router.put(
    "/{lesson_id}/publish",
    response_model=PublishLessonResponse,
    summary="Publish lesson",
    description="Change lesson status from draft to published",
    responses={
        404: {"description": "Lesson not found"},
        400: {"description": "Lesson already published"},
        403: {"description": "Not authorized (teacher only)"},
    },
)
async def publish_lesson(
    lesson_id: str,
    current_user = Depends(teacher_required),
    db: Session = Depends(get_db),
) -> PublishLessonResponse:
    """
    Publish a lesson, changing its status from draft to published.
    
    Returns:
    - Updated lesson with published status and timestamp
    
    Note: Requires teacher role
    """
    logger.info(f"📝 Publishing lesson: {lesson_id}")
    
    try:
        # TODO: Add teacher authorization
        # if current_user["role"] not in ["admin", "teacher"]:
        #     raise HTTPException(status_code=403, detail="Not authorized")
        
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        
        if not lesson:
            logger.warning(f"⚠️ Lesson not found: {lesson_id}")
            raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} not found")
        
        if lesson.status == LessonStatus.PUBLISHED:
            logger.warning(f"⚠️ Lesson already published: {lesson_id}")
            raise HTTPException(
                status_code=400,
                detail="Lesson is already published"
            )
        
        # Publish lesson
        lesson.status = LessonStatus.PUBLISHED
        lesson.published_at = datetime.utcnow()
        
        db.commit()
        db.refresh(lesson)
        
        logger.info(f"✅ Lesson published: {lesson_id}")
        
        return PublishLessonResponse(
            lesson_id=lesson.id,
            title=lesson.title,
            status=lesson.status.value,
            published_at=lesson.published_at,
            message="Lesson published successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error publishing lesson: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to publish lesson")


@router.post(
    "/{lesson_id}/rate",
    summary="Rate lesson",
    description="Submit a rating for a lesson",
    responses={
        404: {"description": "Lesson not found"},
        400: {"description": "Invalid rating (must be 1-5)"},
    },
)
async def rate_lesson(
    lesson_id: str,
    request: RateLessonRequest = Body(..., description="Rating"),
    current_user = Depends(student_required),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Rate a lesson on a scale of 1-5 stars.
    """
    logger.info(f"⭐ Rating lesson: {lesson_id}, rating={request.rating}")
    
    try:
        # TODO: Add student authorization
        # if current_user["role"] != "student":
        #    pass
        
        # Validate rating
        if not (1.0 <= request.rating <= 5.0):
            logger.warning(f"⚠️ Invalid rating: {request.rating}")
            raise HTTPException(
                status_code=400,
                detail="Rating must be between 1.0 and 5.0"
            )
        
        lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
        
        if not lesson:
            logger.warning(f"⚠️ Lesson not found: {lesson_id}")
            raise HTTPException(status_code=404, detail=f"Lesson {lesson_id} not found")
        
        # Update rating (simple average)
        current_avg = lesson.avg_rating or 0
        current_count = getattr(lesson, 'rating_count', 0)
        
        new_avg = (current_avg * current_count + request.rating) / (current_count + 1)
        
        lesson.avg_rating = round(new_avg, 2)
        if hasattr(lesson, 'rating_count'):
            lesson.rating_count = current_count + 1
        
        db.commit()
        db.refresh(lesson)
        
        logger.info(
            f"✅ Lesson rated: {lesson_id}, "
            f"new avg: {lesson.avg_rating}"
        )
        
        return {
            "lesson_id": lesson.id,
            "avg_rating": lesson.avg_rating,
            "rating_count": getattr(lesson, 'rating_count', 1),
            "message": "Lesson rated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error rating lesson: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to rate lesson")


@router.get(
    "/recent",
    response_model=LessonsListResponse,
    summary="Get recent lessons",
    description="Retrieve the most recently published lessons",
)
async def get_recent_lessons(
    limit: int = Query(20, ge=1, le=100, description="Number of lessons to return"),
    db: Session = Depends(get_db),
) -> LessonsListResponse:
    """
    Get the 20 most recently published lessons.
    """
    logger.info(f"📚 Fetching recent lessons (limit={limit})")
    
    try:
        lessons = (
            db.query(Lesson)
            .filter(Lesson.status == LessonStatus.PUBLISHED)
            .order_by(desc(Lesson.published_at))
            .limit(limit if limit < 20 else 20)
            .all()
        )
        
        logger.info(f"✅ Retrieved {len(lessons)} recent lessons")
        
        items = []
        for l in lessons:
            items.append(
                LessonResponse(
                    id=l.id,
                    title=l.title,
                    summary=l.summary,
                    status=l.status.value,
                    difficulty_levels=[lv for lv in VALID_LEVELS if getattr(l, f"{lv}_content") is not None],
                    subjects=l.subjects,
                    source_article_id=l.news_article_id,
                    views_count=l.views_count,
                    avg_rating=l.avg_rating,
                    rating_count=getattr(l, 'rating_count', 0),
                    created_at=l.created_at,
                    published_at=l.published_at
                )
            )

        return LessonsListResponse(
            items=items,
            total=len(items),
            limit=limit,
            offset=0,
        )
    
    except Exception as e:
        logger.error(f"❌ Error fetching recent lessons: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch recent lessons")


@router.get(
    "/search",
    response_model=LessonsListResponse,
    summary="Search lessons",
    description="Search lessons by title, summary, or subject",
)
async def search_lessons(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> LessonsListResponse:
    """
    Search lessons by title, summary, or STEM subject.
    """
    logger.info(f"🔍 Searching lessons: q='{q}', limit={limit}")
    
    try:
        search_term = f"%{q.lower()}%"
        
        query = db.query(Lesson).filter(
            and_(
                Lesson.status == LessonStatus.PUBLISHED,
                or_(
                    Lesson.title.ilike(search_term),
                    Lesson.summary.ilike(search_term),
                    # Simplified subject search in JSON column
                    Lesson.subjects.contains(q)
                )
            )
        )
        
        total = query.count()
        
        lessons = (
            query.order_by(desc(Lesson.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        logger.info(f"✅ Found {len(lessons)} matching lessons (total: {total})")
        
        items = []
        for l in lessons:
             items.append(
                LessonResponse(
                    id=l.id,
                    title=l.title,
                    summary=l.summary,
                    status=l.status.value,
                    difficulty_levels=[lv for lv in VALID_LEVELS if getattr(l, f"{lv}_content") is not None],
                    subjects=l.subjects,
                    source_article_id=l.news_article_id,
                    views_count=l.views_count,
                    avg_rating=l.avg_rating,
                    rating_count=getattr(l, 'rating_count', 0),
                    created_at=l.created_at,
                    published_at=l.published_at
                )
            )

        return LessonsListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
    
    except Exception as e:
        logger.error(f"❌ Error searching lessons: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed")
