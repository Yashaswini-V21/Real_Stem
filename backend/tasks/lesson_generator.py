"""Celery task for lesson generation"""
import logging

logger = logging.getLogger(__name__)


async def generate_lesson(topic: str, level: int):
    """Celery task to generate lesson"""
    try:
        logger.info(f"Generating lesson for {topic} at level {level}")
        # Implementation here
    except Exception as e:
        logger.error(f"Error generating lesson: {e}")
        raise


async def generate_assessment(lesson_id: str):
    """Celery task to generate assessment"""
    try:
        logger.info(f"Generating assessment for lesson {lesson_id}")
        # Implementation here
    except Exception as e:
        logger.error(f"Error generating assessment: {e}")
        raise
