"""
AI Lesson Generator Service

Generates comprehensive, multi-level STEM lessons from news articles using
Claude AI and Google Gemini with adaptive content, videos, simulations, and career paths.
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import anthropic
import google.generativeai as genai

from config import settings
from models.lesson import Lesson, LessonStatus
from models.news import NewsArticle
from utils.logger import get_logger

logger = get_logger(__name__)


class AILessonGenerator:
    """
    Generates AI-powered adaptive STEM lessons from news articles.
    
    Features:
    - Multi-level content generation (elementary → college)
    - Automatic subject extraction and standards alignment
    - Video script and simulation generation
    - Career path recommendations
    - Claude + Gemini API fallback
    """
    
    # STEM subject classifications
    STEM_SUBJECTS = [
        "Physics", "Chemistry", "Biology", "Mathematics", "Computer Science",
        "Engineering", "Astronomy", "Geology", "Environmental Science",
        "Technology", "Robotics", "AI/ML", "Data Science"
    ]
    
    # Difficulty levels
    LEVELS = ["elementary", "middle_school", "high_school", "advanced", "college"]
    
    # Standards organizations
    STANDARDS = {
        "NGSS": "Next Generation Science Standards",
        "CCSS": "Common Core State Standards",
        "ISTE": "International Society for Technology in Education"
    }
    
    def __init__(self):
        """Initialize AI clients and load prompt templates"""
        try:
            # Initialize Anthropic Claude
            self.claude_client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)
            logger.info("✅ Claude API client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Claude: {e}")
            self.claude_client = None
        
        try:
            # Initialize Google Gemini
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel("gemini-pro")
            logger.info("✅ Gemini API client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.gemini_model = None
        
        # Load prompt templates
        self.prompts = {}
        self._load_prompts()
        logger.info("📰 AILessonGenerator initialized")
    
    def _load_prompts(self) -> None:
        """Load prompt templates from prompts folder"""
        prompts_dir = Path(__file__).parent.parent / "prompts"
        
        prompt_files = {
            "lesson_generator": "lesson_generator.txt",
            "video_script": "video_script.txt",
            "assessment_creator": "assessment_creator.txt",
            "career_connector": "career_connector.txt",
        }
        
        for key, filename in prompt_files.items():
            filepath = prompts_dir / filename
            try:
                if filepath.exists():
                    with open(filepath, 'r') as f:
                        self.prompts[key] = f.read()
                    logger.debug(f"✅ Loaded prompt: {key}")
                else:
                    logger.warning(f"⚠️ Prompt file not found: {filepath}")
                    # Use default prompt template
                    self.prompts[key] = self._get_default_prompt(key)
            except Exception as e:
                logger.error(f"❌ Error loading prompt {key}: {e}")
                self.prompts[key] = self._get_default_prompt(key)
    
    def _get_default_prompt(self, key: str) -> str:
        """Get default prompt template if file not found"""
        defaults = {
            "lesson_generator": (
                "Create a {difficulty_level} STEM lesson based on this news article:\n"
                "Title: {news_title}\n"
                "Content: {news_content}\n"
                "Provide JSON with: learning_objectives, key_concepts, activities, assessment"
            ),
            "video_script": (
                "Write a {difficulty_level} level video script for these concepts: {concepts}\n"
                "Based on: {news_title}\n"
                "Format: Simple, engaging, 3-5 minutes duration"
            ),
            "assessment_creator": (
                "Create {difficulty_level} assessment questions for: {concepts}\n"
                "Provide: 5 multiple choice and 2 short answer questions"
            ),
            "career_connector": (
                "What careers use these STEM concepts: {concepts}\n"
                "Provide JSON with: career_title, description, salary_range, required_skills"
            ),
        }
        return defaults.get(key, "")
    
    async def generate_complete_lesson(
        self,
        news_article: NewsArticle,
        user_id: str = None,
        use_breaking_news_mode: bool = False
    ) -> Lesson:
        """
        Generate a complete multi-level lesson from a news article.
        
        Args:
            news_article: NewsArticle model instance
            user_id: Creator user ID
            use_breaking_news_mode: Fast generation for breaking news
            
        Returns:
            Complete Lesson object ready for database insertion
        """
        logger.info(f"🤖 Generating complete lesson from: {news_article.title}")
        
        try:
            # Generate content for each level
            content_dict = {}
            for level in self.LEVELS:
                logger.info(f"🤖 Generating {level} content...")
                level_content = await self._generate_level_content(
                    news_article, level, use_breaking_news_mode
                )
                content_dict[f"{level}_content"] = level_content
            
            # Extract subjects from news article
            subjects = self._extract_subjects(news_article)
            logger.info(f"✅ Extracted subjects: {subjects}")
            
            # Align to standards
            standards = self._align_standards(subjects)
            logger.info(f"✅ Aligned to standards: {standards}")
            
            # Generate career paths
            career_paths = await self._generate_career_paths(news_article, subjects)
            logger.info(f"✅ Generated {len(career_paths)} career paths")
            
            # Generate title and summary
            title = self._generate_title(news_article)
            summary = self._generate_summary(news_article, subjects)
            
            # Create Lesson object
            lesson = Lesson(
                title=title,
                summary=summary,
                news_article_id=news_article.id if hasattr(news_article, 'id') else None,
                created_by=user_id,
                **content_dict,
                subjects=subjects,
                standards_aligned=standards,
                career_paths=career_paths,
                status=LessonStatus.PUBLISHED if use_breaking_news_mode else LessonStatus.DRAFT,
                generated_at=datetime.utcnow(),
                metadata={
                    "ai_model": "claude-sonnet-4",
                    "breaking_news_mode": use_breaking_news_mode,
                    "source_url": news_article.url,
                    "confidence": news_article.stem_confidence,
                }
            )
            
            logger.info(f"✅ Lesson generation complete: {title}")
            return lesson
        
        except Exception as e:
            logger.error(f"❌ Error generating lesson: {e}", exc_info=True)
            raise
    
    async def _generate_level_content(
        self,
        news_article: NewsArticle,
        level: str,
        breaking_news: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content for a specific educational level.
        
        Args:
            news_article: Source news article
            level: Educational level (elementary, middle_school, etc.)
            breaking_news: Fast generation mode
            
        Returns:
            Dictionary with content, objectives, concepts, activities, assessment
        """
        try:
            # Build prompt
            prompt = self.prompts.get("lesson_generator", "")
            prompt = prompt.format(
                difficulty_level=level.replace("_", " ").title(),
                news_title=news_article.title,
                news_content=news_article.content[:1000]  # First 1000 chars
            )
            
            # Call Claude API
            logger.debug(f"📡 Calling Claude for {level} content...")
            response = await self._call_claude(prompt, max_tokens=4000)
            
            if not response:
                # Fallback to Gemini
                logger.warning(f"⚠️ Claude failed, trying Gemini for {level}")
                response = await self._call_gemini(prompt)
            
            # Parse response
            try:
                content_data = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                content_data = self._extract_json(response)
            
            # Generate video script
            key_concepts = content_data.get("key_concepts", [])
            video_script = await self._generate_video_script(
                news_article, level, key_concepts
            )
            
            # Generate simulation spec
            simulation_spec = self._generate_simulation_spec(news_article, level)
            
            # Build final content
            level_content = {
                "content": content_data.get("content", response),
                "learning_objectives": content_data.get("learning_objectives", []),
                "key_concepts": key_concepts,
                "activities": content_data.get("activities", []),
                "assessment": content_data.get("assessment", {}),
                "estimated_time_minutes": 45 if level == "elementary" else 60,
                "video_script": video_script,
                "simulation_spec": simulation_spec,
            }
            
            return level_content
        
        except Exception as e:
            logger.error(f"❌ Error generating {level} content: {e}")
            return {"content": "", "learning_objectives": [], "key_concepts": []}
    
    async def _generate_video_script(
        self,
        news_article: NewsArticle,
        level: str,
        key_concepts: List[str]
    ) -> str:
        """
        Generate video script for lesson content.
        
        Args:
            news_article: Source article
            level: Educational level
            key_concepts: Main concepts to cover
            
        Returns:
            Video script text
        """
        try:
            prompt = self.prompts.get("video_script", "")
            prompt = prompt.format(
                difficulty_level=level.replace("_", " ").title(),
                concepts=", ".join(key_concepts),
                news_title=news_article.title
            )
            
            response = await self._call_claude(prompt, max_tokens=2000)
            if not response:
                response = await self._call_gemini(prompt)
            
            return response or f"Video script for {level} level: {', '.join(key_concepts)}"
        
        except Exception as e:
            logger.error(f"❌ Error generating video script: {e}")
            return ""
    
    def _generate_simulation_spec(
        self,
        news_article: NewsArticle,
        level: str
    ) -> Dict[str, Any]:
        """
        Generate specification for interactive simulation.
        
        Args:
            news_article: Source article
            level: Educational level
            
        Returns:
            Simulation specification dictionary
        """
        try:
            topics = news_article.topics if hasattr(news_article, 'topics') else []
            topics_lower = [t.lower() for t in topics] if topics else []
            
            # Determine simulation type based on topics
            sim_type = "general"
            engine = "phaser"  # Default game engine
            
            if any(term in str(topics_lower) for term in ["physics", "force", "motion", "gravity"]):
                sim_type = "physics"
                engine = "cannon.js"
            elif any(term in str(topics_lower) for term in ["chemistry", "molecule", "reaction"]):
                sim_type = "chemistry"
                engine = "babylon.js"
            elif any(term in str(topics_lower) for term in ["biology", "cell", "organism"]):
                sim_type = "biology"
                engine = "babylon.js"
            elif any(term in str(topics_lower) for term in ["math", "geometry", "algebra"]):
                sim_type = "math"
                engine = "pixi.js"
            
            spec = {
                "type": sim_type,
                "engine": engine,
                "difficulty_level": level,
                "parameters": {
                    "duration_minutes": 10 if level == "elementary" else 15,
                    "interactive": True,
                    "difficulty_scaling": True,
                },
                "learning_outcomes": [
                    "Understand core concepts",
                    "Practice application",
                    "Measure results"
                ]
            }
            
            return spec
        
        except Exception as e:
            logger.error(f"❌ Error generating simulation spec: {e}")
            return {"type": "general", "engine": "phaser"}
    
    async def _generate_career_paths(
        self,
        news_article: NewsArticle,
        subjects: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate career path recommendations.
        
        Args:
            news_article: Source article
            subjects: STEM subjects covered
            
        Returns:
            List of career path dictionaries
        """
        try:
            prompt = self.prompts.get("career_connector", "")
            prompt = prompt.format(concepts=", ".join(subjects))
            
            response = await self._call_claude(prompt, max_tokens=2000)
            if not response:
                response = await self._call_gemini(prompt)
            
            # Parse JSON response
            try:
                careers_data = json.loads(response)
                if isinstance(careers_data, dict) and "careers" in careers_data:
                    return careers_data["careers"]
            except json.JSONDecodeError:
                pass
            
            # Return default career paths
            return [
                {
                    "title": subject + " Engineer",
                    "description": f"Build applications using {subject}",
                    "salary_range": "$80,000 - $150,000",
                    "required_skills": [subject, "Problem Solving", "Communication"]
                }
                for subject in subjects[:3]
            ]
        
        except Exception as e:
            logger.error(f"❌ Error generating career paths: {e}")
            return []
    
    def _extract_subjects(self, news_article: NewsArticle) -> List[str]:
        """
        Extract STEM subjects from news article.
        
        Args:
            news_article: Source article
            
        Returns:
            List of identified subjects
        """
        try:
            subjects = []
            topics = news_article.topics if hasattr(news_article, 'topics') else []
            title = (news_article.title or "").lower()
            content = (news_article.content or "").lower()
            
            # Check topics and content for subject keywords
            for subject in self.STEM_SUBJECTS:
                keywords = subject.lower().split()
                if any(keyword in topics for keyword in keywords) or \
                   any(keyword in title for keyword in keywords) or \
                   any(keyword in content for keyword in keywords):
                    subjects.append(subject)
            
            # Ensure at least one subject
            if not subjects:
                if topics:
                    subjects = [str(t) for t in topics[:3]]
                else:
                    subjects = ["Science", "Technology"]
            
            return list(set(subjects[:5]))  # Max 5 unique subjects
        
        except Exception as e:
            logger.error(f"❌ Error extracting subjects: {e}")
            return ["STEM"]
    
    def _align_standards(self, subjects: List[str]) -> List[str]:
        """
        Align lesson to educational standards.
        
        Args:
            subjects: STEM subjects
            
        Returns:
            List of aligned standard codes
        """
        try:
            standards = []
            
            # Map subjects to standards
            if any(s.lower() in ["physics", "chemistry", "biology"] for s in subjects):
                standards.append("NGSS-PS2-1")  # Forces and motion
                standards.append("NGSS-LS1-1")  # Life structures
            
            if any(s.lower() in ["computer science", "ai/ml", "technology"] for s in subjects):
                standards.append("ISTE-1c")  # Technology integration
                standards.append("CCSS.MATH.MP.2")  # Mathematical reasoning
            
            if any(s.lower() in ["engineering", "robotics"] for s in subjects):
                standards.append("NGSS-ETS1")  # Engineering design
            
            # Always include core standards
            if not standards:
                standards = ["NGSS-PS1-1", "CCSS.MATH.MP.1"]
            
            return list(set(standards[:5]))
        
        except Exception as e:
            logger.error(f"❌ Error aligning standards: {e}")
            return []
    
    def _generate_title(self, news_article: NewsArticle) -> str:
        """Generate lesson title from news article"""
        try:
            # Use original title, truncate if needed
            title = news_article.title[:100] if news_article.title else "STEM Lesson"
            return f"Lesson: {title}"
        except Exception as e:
            logger.error(f"❌ Error generating title: {e}")
            return "STEM Lesson"
    
    def _generate_summary(self, news_article: NewsArticle, subjects: List[str]) -> str:
        """Generate lesson summary"""
        try:
            summary = (
                f"Learn about {', '.join(subjects)} through the lens of: "
                f"{news_article.title}. This adaptive lesson covers concepts "
                f"across all educational levels from elementary to college."
            )
            return summary
        except Exception as e:
            logger.error(f"❌ Error generating summary: {e}")
            return "Adaptive STEM lesson"
    
    async def _call_claude(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """
        Call Claude API.
        
        Args:
            prompt: Prompt text
            max_tokens: Maximum tokens in response
            
        Returns:
            Response text or None
        """
        try:
            if not self.claude_client:
                logger.warning("⚠️ Claude client not available")
                return None
            
            message = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        
        except Exception as e:
            logger.error(f"❌ Claude API error: {e}")
            return None
    
    async def _call_gemini(self, prompt: str) -> Optional[str]:
        """
        Call Gemini API as fallback.
        
        Args:
            prompt: Prompt text
            
        Returns:
            Response text or None
        """
        try:
            if not self.gemini_model:
                logger.warning("⚠️ Gemini model not available")
                return None
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}")
            return None
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from text response.
        
        Args:
            text: Response text
            
        Returns:
            Parsed JSON dictionary
        """
        try:
            # Try to find JSON block
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx + 1]
                return json.loads(json_str)
        except Exception as e:
            logger.debug(f"⚠️ Could not extract JSON: {e}")
        
        return {"content": text}


# Singleton instance
ai_generator = AILessonGenerator()
