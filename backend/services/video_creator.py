"""
Video Creator Service

Generates educational videos from lesson scripts using Google Cloud Text-to-Speech
and MoviePy, combining audio narration with visual content and subtitles.
"""
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import logging

from google.cloud import texttospeech
import moviepy.editor as mpy
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VideoCreator:
    """
    Creates educational videos from lesson scripts.
    
    Features:
    - Text-to-speech audio generation using Google Cloud TTS
    - Video composition with MoviePy
    - Subtitle/caption support
    - Cloud storage integration
    - Multiple audio voices and languages
    """
    
    # TTS Voice configurations
    VOICES = {
        "elementary": {
            "language_code": "en-US",
            "ssml_gender": texttospeech.SsmlVoiceGender.FEMALE,
            "name": "en-US-Neural2-C",  # Friendly female voice
        },
        "middle_school": {
            "language_code": "en-US",
            "ssml_gender": texttospeech.SsmlVoiceGender.NEUTRAL,
            "name": "en-US-Neural2-E",  # Neutral voice
        },
        "high_school": {
            "language_code": "en-US",
            "ssml_gender": texttospeech.SsmlVoiceGender.MALE,
            "name": "en-US-Neural2-A",  # Professional male voice
        },
        "advanced": {
            "language_code": "en-US",
            "ssml_gender": texttospeech.SsmlVoiceGender.MALE,
            "name": "en-US-Neural2-A",
        },
        "college": {
            "language_code": "en-US",
            "ssml_gender": texttospeech.SsmlVoiceGender.MALE,
            "name": "en-US-Neural2-A",
        },
    }
    
    # Video settings
    VIDEO_WIDTH = 1280
    VIDEO_HEIGHT = 720
    VIDEO_FPS = 30
    VIDEO_DURATION = 300  # 5 minutes max
    
    def __init__(self):
        """Initialize Google Cloud TTS client and setup directories"""
        try:
            # Initialize Google Cloud TTS client
            self.tts_client = texttospeech.TextToSpeechClient()
            logger.info("✅ Google Cloud TTS client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Cloud TTS: {e}")
            self.tts_client = None
        
        # Setup media directories
        self.media_dir = Path(settings.MEDIA_PATH) if hasattr(settings, 'MEDIA_PATH') else Path("media")
        self.videos_dir = self.media_dir / "videos"
        self.audio_dir = self.media_dir / "audio"
        self.temp_dir = self.media_dir / "temp"
        
        # Create directories if they don't exist
        for directory in [self.media_dir, self.videos_dir, self.audio_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📁 Media directory ready: {directory}")
        
        logger.info("🎬 VideoCreator initialized")
    
    async def create_video_from_script(
        self,
        script_text: str,
        difficulty_level: str,
        lesson_id: str,
        lesson_title: str = "STEM Lesson"
    ) -> Optional[str]:
        """
        Create a complete video from lesson script.
        
        Args:
            script_text: Video script text (narration)
            difficulty_level: Educational level (elementary, middle_school, etc.)
            lesson_id: Unique lesson identifier
            lesson_title: Title for the video
            
        Returns:
            URL to the created video or None on failure
        """
        logger.info(f"🎬 Starting video creation for lesson: {lesson_id}")
        
        try:
            # Generate audio from script
            logger.info("🔊 Generating audio from script...")
            audio_path = await self._generate_audio(script_text, difficulty_level)
            
            if not audio_path:
                logger.error("❌ Failed to generate audio")
                return None
            
            # Create video with audio and visuals
            logger.info("🎨 Creating video with audio and visuals...")
            video_path = await self._create_video_with_audio(
                audio_path,
                lesson_title,
                difficulty_level,
                script_text
            )
            
            if not video_path:
                logger.error("❌ Failed to create video")
                return None
            
            # Upload to storage
            logger.info("☁️ Uploading video to storage...")
            video_url = await self._upload_to_storage(video_path, lesson_id, difficulty_level)
            
            # Cleanup temporary files
            self._cleanup_temp_files(audio_path, video_path)
            
            logger.info(f"✅ Video creation complete: {video_url}")
            return video_url
        
        except Exception as e:
            logger.error(f"❌ Error creating video: {e}", exc_info=True)
            return None
    
    async def _generate_audio(
        self,
        text: str,
        difficulty_level: str = "middle_school"
    ) -> Optional[str]:
        """
        Generate audio from text using Google Cloud Text-to-Speech.
        
        Args:
            text: Script text to convert to speech
            difficulty_level: Educational level (determines voice)
            
        Returns:
            Path to audio file or None on failure
        """
        logger.info(f"🔊 Generating audio for {difficulty_level} level...")
        
        try:
            if not self.tts_client:
                logger.error("❌ TTS client not available")
                return None
            
            # Get voice configuration for difficulty level
            voice_config = self.VOICES.get(difficulty_level, self.VOICES["middle_school"])
            
            # Prepare synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Select voice and audio encoding
            voice = texttospeech.VoiceSelectionParams(
                language_code=voice_config["language_code"],
                ssml_gender=voice_config["ssml_gender"],
                name=voice_config["name"],
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=0.95,  # Slightly slower for clarity
                pitch=0.0,  # Normal pitch
            )
            
            # Call TTS API
            logger.debug("📡 Calling Google Cloud TTS API...")
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config,
            )
            
            # Save audio file
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            audio_path = self.audio_dir / f"audio_{difficulty_level}_{timestamp}.mp3"
            
            with open(audio_path, "wb") as audio_file:
                audio_file.write(response.audio_content)
            
            logger.info(f"✅ Audio generated: {audio_path}")
            return str(audio_path)
        
        except Exception as e:
            logger.error(f"❌ Error generating audio: {e}")
            return None
    
    async def _create_video_with_audio(
        self,
        audio_path: str,
        title: str,
        difficulty_level: str,
        script_text: str
    ) -> Optional[str]:
        """
        Create video by combining audio with visual content.
        
        Args:
            audio_path: Path to audio file
            title: Video title
            difficulty_level: Educational level
            script_text: Original script (for subtitles)
            
        Returns:
            Path to created video or None on failure
        """
        logger.info("🎨 Creating video composition...")
        
        try:
            # Load audio to get duration
            audio_clip = mpy.AudioFileClip(audio_path)
            duration = audio_clip.duration
            logger.info(f"⏱️ Audio duration: {duration:.1f} seconds")
            
            # Create background color clip with gradient effect
            background = mpy.ColorClip(
                size=(self.VIDEO_WIDTH, self.VIDEO_HEIGHT),
                color=(20, 30, 60)  # Dark blue background
            ).set_duration(duration)
            
            # Add title text at the beginning
            title_clip = self._create_title_clip(title, duration)
            
            # Create animated visuals (simple geometry or gradient)
            visuals_clip = self._create_visual_elements(duration)
            
            # Composite video
            if visuals_clip:
                video = mpy.CompositeVideoClip(
                    [background, visuals_clip, title_clip],
                    size=(self.VIDEO_WIDTH, self.VIDEO_HEIGHT)
                )
            else:
                video = mpy.CompositeVideoClip(
                    [background, title_clip],
                    size=(self.VIDEO_WIDTH, self.VIDEO_HEIGHT)
                )
            
            # Add audio
            video_with_audio = video.set_audio(audio_clip)
            
            # Add subtitles (optional - for accessibility)
            video_with_subtitles = await self._add_subtitles(
                video_with_audio,
                script_text,
                duration
            )
            
            # Write video file
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = self.videos_dir / f"lesson_{difficulty_level}_{timestamp}.mp4"
            
            logger.info(f"📝 Writing video to: {output_path}")
            video_with_subtitles.write_videofile(
                str(output_path),
                fps=self.VIDEO_FPS,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None  # Suppress MoviePy logs
            )
            
            logger.info(f"✅ Video created: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"❌ Error creating video: {e}")
            return None
    
    def _create_title_clip(self, title: str, duration: float):
        """
        Create animated title text clip.
        
        Args:
            title: Title text
            duration: Clip duration
            
        Returns:
            Text clip object
        """
        try:
            # Title appears for first 3 seconds
            title_duration = min(3.0, duration)
            
            title_clip = mpy.TextClip(
                txt=title,
                fontsize=60,
                color="white",
                font="Arial-Bold",
                align="center",
                method="caption",
                size=(self.VIDEO_WIDTH - 100, None)
            )
            
            # Center and set duration
            title_clip = title_clip.set_duration(title_duration)
            title_clip = title_clip.set_position("center")
            
            # Fade in and out
            title_clip = title_clip.crossfadeout(0.5)
            
            return title_clip
        
        except Exception as e:
            logger.warning(f"⚠️ Could not create title clip: {e}")
            return None
    
    def _create_visual_elements(self, duration: float):
        """
        Create animated visual elements for the video.
        
        Args:
            duration: Video duration
            
        Returns:
            Video clip with animations or None
        """
        try:
            # Create simple animated shapes
            # You can replace this with more sophisticated animations
            
            # Create a gradient animation effect
            def make_frame(t):
                """Create frame with animated gradient"""
                import numpy as np
                
                # Create gradient from top to bottom
                height = self.VIDEO_HEIGHT
                width = self.VIDEO_WIDTH
                
                # Animated wave effect
                gradient = np.zeros((height, width, 3), dtype=np.uint8)
                for y in range(height):
                    # Animated color cycling
                    hue = (y / height + t / 10) % 1.0
                    # Convert HSV to RGB (simplified)
                    r = int(255 * (0.5 + 0.5 * np.sin(hue * np.pi)))
                    g = int(255 * (0.5 + 0.5 * np.sin((hue + 0.33) * np.pi)))
                    b = int(255 * (0.5 + 0.5 * np.sin((hue + 0.66) * np.pi)))
                    gradient[y, :] = [r, g, b]
                
                return gradient
            
            # Create animation clip
            animation = mpy.VideoClip(make_frame, duration=duration)
            animation.fps = self.VIDEO_FPS
            
            # Reduce opacity for subtle effect
            animation = animation.set_opacity(0.3)
            
            return animation
        
        except Exception as e:
            logger.warning(f"⚠️ Could not create visual elements: {e}")
            return None
    
    async def _add_subtitles(
        self,
        video_clip,
        script_text: str,
        duration: float
    ):
        """
        Add subtitles to video for accessibility.
        
        Args:
            video_clip: Video clip object
            script_text: Script text for subtitles
            duration: Total duration
            
        Returns:
            Video with subtitles
        """
        try:
            # Split script into chunks for subtitles
            words = script_text.split()
            chunk_size = 10  # Words per subtitle
            chunks = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
            
            # Calculate timing for each subtitle
            time_per_chunk = duration / len(chunks) if chunks else 0
            
            subtitle_clips = []
            for i, chunk in enumerate(chunks):
                start_time = i * time_per_chunk
                end_time = (i + 1) * time_per_chunk
                
                subtitle = mpy.TextClip(
                    txt=chunk,
                    fontsize=24,
                    color="white",
                    font="Arial",
                    bg_color="black",
                    align="center",
                    size=(self.VIDEO_WIDTH - 50, None)
                )
                
                subtitle = subtitle.set_duration(end_time - start_time)
                subtitle = subtitle.set_start(start_time)
                subtitle = subtitle.set_position(("center", "bottom"))
                
                subtitle_clips.append(subtitle)
            
            # Composite video with subtitles
            if subtitle_clips:
                video_with_subtitles = mpy.CompositeVideoClip(
                    [video_clip] + subtitle_clips
                )
                return video_with_subtitles
            
            return video_clip
        
        except Exception as e:
            logger.warning(f"⚠️ Could not add subtitles: {e}")
            return video_clip
    
    async def _upload_to_storage(
        self,
        video_path: str,
        lesson_id: str,
        difficulty_level: str
    ) -> Optional[str]:
        """
        Upload video to cloud storage or local storage.
        
        Args:
            video_path: Local video file path
            lesson_id: Lesson ID for organization
            difficulty_level: Educational level
            
        Returns:
            Public URL to the video or None on failure
        """
        try:
            # For development, use local storage
            # In production, would upload to Google Cloud Storage, S3, etc.
            
            if settings.ENVIRONMENT == "production":
                # TODO: Implement cloud storage upload
                # Example: Google Cloud Storage, AWS S3, etc.
                logger.warning("⚠️ Production storage not implemented, using local storage")
            
            # For now, use local file serving
            video_filename = f"{lesson_id}_{difficulty_level}.mp4"
            public_path = f"/api/media/videos/{video_filename}"
            
            # Copy to final location
            final_path = self.videos_dir / video_filename
            
            try:
                import shutil
                shutil.copy(video_path, final_path)
                logger.info(f"✅ Video stored locally: {final_path}")
            except Exception as e:
                logger.error(f"❌ Error copying video: {e}")
                return None
            
            logger.info(f"✅ Video URL: {public_path}")
            return public_path
        
        except Exception as e:
            logger.error(f"❌ Error uploading video: {e}")
            return None
    
    def _cleanup_temp_files(self, *file_paths: str) -> None:
        """
        Clean up temporary files.
        
        Args:
            file_paths: Paths of temporary files to delete
        """
        try:
            for file_path in file_paths:
                if file_path and Path(file_path).exists():
                    try:
                        Path(file_path).unlink()
                        logger.debug(f"🧹 Cleaned up: {file_path}")
                    except Exception as e:
                        logger.warning(f"⚠️ Could not delete {file_path}: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup error: {e}")
    
    async def get_video_thumbnail(
        self,
        video_path: str,
        time_offset: float = 2.0
    ) -> Optional[str]:
        """
        Extract thumbnail from video.
        
        Args:
            video_path: Path to video file
            time_offset: Time offset in seconds
            
        Returns:
            Path to thumbnail image or None
        """
        try:
            video = mpy.VideoFileClip(video_path)
            
            # Clamp time offset to video duration
            time_offset = min(time_offset, video.duration - 0.1)
            
            # Get frame at specified time
            frame = video.get_frame(time_offset)
            
            # Save thumbnail
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            thumbnail_path = self.media_dir / f"thumbnail_{timestamp}.jpg"
            
            import imageio
            imageio.imwrite(thumbnail_path, frame)
            
            logger.info(f"✅ Thumbnail created: {thumbnail_path}")
            return str(thumbnail_path)
        
        except Exception as e:
            logger.error(f"❌ Error creating thumbnail: {e}")
            return None


# Singleton instance
video_creator = VideoCreator()
