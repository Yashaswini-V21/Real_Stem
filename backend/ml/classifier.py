"""
STEM Relevance Classifier

Classifies educational content for STEM relevance using pre-trained BERT model
with fallback to keyword-based classification.
"""
import pickle
import json
from pathlib import Path
from typing import Tuple, List, Dict, Optional, Any
from datetime import datetime
import logging

import torch
import numpy as np

try:
    from transformers import (
        DistilBertTokenizer,
        DistilBertForSequenceClassification,
        Trainer,
        TrainingArguments,
        TextClassificationPipeline,
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.preprocessing import LabelEncoder
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class STEMDataset(torch.utils.data.Dataset):
    """PyTorch dataset for STEM classification"""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.encodings = tokenizer(
            texts,
            max_length=max_length,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
        self.labels = torch.tensor(labels)
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return {
            "input_ids": self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels": self.labels[idx],
        }


class STEMClassifier:
    """
    STEM Relevance Classifier using BERT with keyword-based fallback.
    
    Features:
    - Pre-trained DistilBERT for efficient classification
    - Keyword-based fallback when model unavailable
    - Topic extraction from text
    - Model training capabilities
    - GPU/CPU support
    """
    
    # STEM keywords for fallback classification
    STEM_KEYWORDS = {
        "science": ["science", "scientific", "experiment", "hypothesis", "theory", "observation"],
        "technology": ["technology", "software", "hardware", "digital", "computer", "internet", "app", "ai", "machine learning"],
        "engineering": ["engineering", "design", "build", "structure", "mechanism", "system", "circuit", "robot", "automation"],
        "mathematics": ["math", "mathematics", "equation", "calculate", "algebra", "geometry", "calculus", "algorithm", "data"],
        "physics": ["physics", "force", "motion", "gravity", "energy", "wave", "particle", "quantum", "relativity"],
        "chemistry": ["chemistry", "chemical", "reaction", "element", "molecule", "compound", "atom", "periodic"],
        "biology": ["biology", "organism", "cell", "dna", "evolution", "ecosystem", "genetics", "protein"],
        "astronomy": ["astronomy", "space", "planet", "star", "galaxy", "universe", "cosmos", "satellite"],
        "geology": ["geology", "earth", "rock", "mineral", "earthquake", "volcano", "fossil", "plate tectonics"],
        "environmental": ["environmental", "climate", "ecology", "green", "sustainability", "carbon", "pollution"],
        "robotics": ["robot", "robotics", "automation", "control", "sensor", "actuator"],
        "data": ["data", "analysis", "statistics", "database", "big data", "analytics", "prediction"],
        "programming": ["programming", "code", "script", "python", "java", "javascript", "c++", "algorithm"],
    }
    
    STEM_TOPICS = list(STEM_KEYWORDS.keys())
    
    # Device configuration
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def __init__(self):
        """Initialize STEM classifier with pre-trained model or fallback"""
        self.model_path = Path(settings.ML_MODELS_PATH) if hasattr(settings, 'ML_MODELS_PATH') else Path("backend/ml/models")
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.tokenizer = None
        self.model = None
        self.classifier_pipeline = None
        self.use_model = False
        
        # Load pre-trained model
        self._load_model()
        
        logger.info(
            f"✅ STEMClassifier initialized (using {'BERT model' if self.use_model else 'keyword-based fallback'})"
        )
        logger.info(f"📊 Device: {self.DEVICE}")
    
    def _load_model(self) -> None:
        """Load pre-trained BERT model or create fallback"""
        if not TRANSFORMERS_AVAILABLE:
            logger.warning("❌ Transformers library not available, using keyword-based classification")
            return
        
        try:
            model_file = self.model_path / "stem_classifier_model"
            
            if model_file.exists():
                # Load fine-tuned model
                logger.info("📦 Loading fine-tuned STEM classifier model...")
                self.tokenizer = DistilBertTokenizer.from_pretrained(model_file)
                self.model = DistilBertForSequenceClassification.from_pretrained(model_file)
                self.model.to(self.DEVICE)
                self.model.eval()
                
                self.classifier_pipeline = TextClassificationPipeline(
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if torch.cuda.is_available() else -1,
                    framework="pt"
                )
                self.use_model = True
                logger.info("✅ Fine-tuned model loaded successfully")
            else:
                # Load pre-trained DistilBERT
                logger.info("📦 Loading pre-trained DistilBERT model...")
                self.tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
                self.model = DistilBertForSequenceClassification.from_pretrained(
                    "distilbert-base-uncased",
                    num_labels=2  # Binary classification: STEM vs Non-STEM
                )
                self.model.to(self.DEVICE)
                self.model.eval()
                
                self.classifier_pipeline = TextClassificationPipeline(
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=0 if torch.cuda.is_available() else -1,
                    framework="pt"
                )
                self.use_model = True
                logger.info("✅ Pre-trained DistilBERT loaded successfully")
        
        except Exception as e:
            logger.warning(f"⚠️ Could not load BERT model: {e}")
            logger.info("💡 Using keyword-based classification as fallback")
            self.use_model = False
    
    def predict(self, text: str) -> Tuple[bool, float]:
        """
        Predict if text is STEM-relevant.
        
        Args:
            text: Article title and content to classify
            
        Returns:
            Tuple of (is_stem: bool, confidence: float 0-1)
        """
        logger.debug(f"🔍 Predicting STEM relevance for text: {text[:100]}...")
        
        try:
            if self.use_model and self.classifier_pipeline:
                # Use BERT model
                result = self.classifier_pipeline(text, truncation=True, max_length=512)[0]
                
                # Extract confidence
                confidence = result["score"]
                # Label: LABEL_0 = non-STEM, LABEL_1 = STEM
                is_stem = result["label"] == "LABEL_1"
                
                logger.debug(f"✅ Model prediction: STEM={is_stem}, confidence={confidence:.2%}")
                return is_stem, confidence
            else:
                # Use keyword-based fallback
                confidence = self._keyword_classify(text)
                is_stem = confidence > 0.5
                
                logger.debug(f"✅ Keyword-based prediction: STEM={is_stem}, confidence={confidence:.2%}")
                return is_stem, confidence
        
        except Exception as e:
            logger.error(f"❌ Error predicting STEM relevance: {e}")
            # Fallback to keyword classification on error
            confidence = self._keyword_classify(text)
            return confidence > 0.5, confidence
    
    def extract_topics(self, text: str) -> List[str]:
        """
        Extract STEM topics from text.
        
        Args:
            text: Text to extract topics from
            
        Returns:
            List of detected STEM topics
        """
        logger.debug(f"🔍 Extracting topics from text: {text[:100]}...")
        
        try:
            text_lower = text.lower()
            found_topics = []
            topic_scores = {}
            
            # Score each topic based on keyword frequency
            for topic, keywords in self.STEM_KEYWORDS.items():
                score = sum(text_lower.count(keyword) for keyword in keywords)
                if score > 0:
                    topic_scores[topic] = score
                    found_topics.append(topic)
            
            # Sort by frequency
            sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
            topics = [topic for topic, _ in sorted_topics]
            
            logger.debug(f"✅ Extracted topics: {topics}")
            return topics
        
        except Exception as e:
            logger.error(f"❌ Error extracting topics: {e}")
            return []
    
    def _keyword_classify(self, text: str) -> float:
        """
        Keyword-based STEM classification (fallback).
        
        Args:
            text: Text to classify
            
        Returns:
            Confidence score (0-1)
        """
        try:
            text_lower = text.lower()
            total_words = len(text_lower.split())
            
            if total_words == 0:
                return 0.0
            
            # Count STEM keyword occurrences
            stem_keyword_count = 0
            topic_matches = {}
            
            for topic, keywords in self.STEM_KEYWORDS.items():
                for keyword in keywords:
                    count = text_lower.count(keyword)
                    if count > 0:
                        stem_keyword_count += count
                        topic_matches[topic] = topic_matches.get(topic, 0) + count
            
            # Calculate confidence
            if stem_keyword_count == 0:
                confidence = 0.0
            else:
                # Normalize by text length and boost for multiple topic matches
                base_confidence = min(stem_keyword_count / (total_words / 10), 1.0)
                topic_diversity_bonus = min(len(topic_matches) / len(self.STEM_KEYWORDS), 0.3)
                confidence = min(base_confidence + topic_diversity_bonus, 1.0)
            
            logger.debug(f"📊 Keyword classification score: {confidence:.2%}")
            return confidence
        
        except Exception as e:
            logger.error(f"❌ Error in keyword classification: {e}")
            return 0.0
    
    def train(
        self,
        training_data: List[Tuple[str, int]],
        num_epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5
    ) -> Dict[str, Any]:
        """
        Train/fine-tune STEM classifier on labeled data.
        
        Args:
            training_data: List of (text, label) tuples where label is 0 (non-STEM) or 1 (STEM)
            num_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate for optimizer
            
        Returns:
            Dictionary with training results
        """
        logger.info(f"🚀 Starting STEM classifier training ({len(training_data)} samples)...")
        
        if not TRANSFORMERS_AVAILABLE:
            logger.error("❌ Transformers library required for training")
            return {"error": "Transformers library not available"}
        
        try:
            if not self.tokenizer or not self.model:
                logger.error("❌ Model not initialized")
                return {"error": "Model not initialized"}
            
            # Prepare data
            texts = [item[0] for item in training_data]
            labels = [item[1] for item in training_data]
            
            logger.info(f"📊 Dataset: {len(texts)} samples, {sum(labels)} STEM, {len(labels) - sum(labels)} non-STEM")
            
            # Create dataset
            dataset = STEMDataset(texts, labels, self.tokenizer)
            
            # Setup training arguments
            training_args = TrainingArguments(
                output_dir=str(self.model_path / "training_results"),
                num_train_epochs=num_epochs,
                per_device_train_batch_size=batch_size,
                save_steps=10,
                save_total_limit=2,
                logging_steps=5,
                learning_rate=learning_rate,
                weight_decay=0.01,
                warmup_steps=100,
            )
            
            # Create trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=dataset,
            )
            
            # Train
            logger.info("⏱️ Training in progress...")
            train_result = trainer.train()
            
            # Save model
            model_save_path = self.model_path / "stem_classifier_model"
            self.model.save_pretrained(model_save_path)
            self.tokenizer.save_pretrained(model_save_path)
            logger.info(f"💾 Model saved to {model_save_path}")
            
            # Save metadata
            metadata = {
                "training_date": str(datetime.now()),
                "num_samples": len(texts),
                "num_epochs": num_epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "training_loss": float(train_result.training_loss),
            }
            
            metadata_path = model_save_path / "metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Training complete! Loss: {train_result.training_loss:.4f}")
            return metadata
        
        except Exception as e:
            logger.error(f"❌ Error training classifier: {e}", exc_info=True)
            return {"error": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current classifier"""
        return {
            "using_model": self.use_model,
            "device": str(self.DEVICE),
            "model_type": "DistilBERT" if self.use_model else "Keyword-based",
            "num_topics": len(self.STEM_TOPICS),
            "topics": self.STEM_TOPICS,
        }


# Singleton instance (lazy-loaded)
_classifier_instance = None


def get_stem_classifier() -> STEMClassifier:
    """Get or create singleton STEM classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = STEMClassifier()
    return _classifier_instance


# Convenience functions
def classify_text(text: str) -> Tuple[bool, float]:
    """Classify text for STEM relevance"""
    classifier = get_stem_classifier()
    return classifier.predict(text)


def extract_stem_topics(text: str) -> List[str]:
    """Extract STEM topics from text"""
    classifier = get_stem_classifier()
    return classifier.extract_topics(text)
