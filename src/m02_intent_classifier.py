"""
Intent classification module for the JUNO Automation Engine.
Wraps the Machine Learning Model for intent prediction.
"""

import os
import re
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


class IntentClassifier:
    """Wraps the Machine Learning Model for prediction."""
    
    def __init__(self, model_dir):
        """
        Initialize the intent classifier by loading the trained model.
        
        Args:
            model_dir (str): Directory containing the model files
        """
        print(f"⏳ Loading models from {model_dir}...")
        
        model_path = os.path.join(model_dir, "intent_classifier.joblib")
        encoder_path = os.path.join(model_dir, "label_encoder.joblib")
        
        try:
            if not os.path.exists(model_path) or not os.path.exists(encoder_path):
                raise FileNotFoundError(
                    f"Missing model files. Expected 'intent_classifier.joblib' and "
                    f"'label_encoder.joblib' in {model_dir}"
                )
            
            self.classifier = joblib.load(model_path)
            self.encoder = joblib.load(encoder_path)
            
            # Using the efficient MiniLM model (matches training)
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize Mood Anchors for Zero-Shot Classification
            self.mood_anchors = {
                "Angry": self.embedder.encode(["I am very angry and upset with this service."])[0],
                "Happy": self.embedder.encode(["I am so happy and satisfied, thank you!"])[0],
                "Urgent": self.embedder.encode(["This is an emergency, I need help immediately."])[0],
                "Confused": self.embedder.encode(["I am confused and don't understand how this works."])[0],
                "Neutral": self.embedder.encode(["Just asking a normal question about my order."])[0]
            }
            
            print(f"✅ AI Engine Ready.")
            
        except Exception as e:
            print(f"❌ AI Engine Failed: {e}")
            self.classifier = None
            self.encoder = None
            self.embedder = None

    def predict(self, text):
        """
        Predict the intent of the given text.
        
        Args:
            text (str): Input text to classify
            
        Returns:
            tuple: (intent, confidence) where intent is a string and confidence is a float
        """
        if not self.classifier:
            return "error", 0.0
        
        # Preprocess
        clean_text = re.sub(r'\s+', ' ', text).strip()
        
        # Vectorize & Predict
        vector = self.embedder.encode([clean_text])
        probs = self.classifier.predict_proba(vector)[0]
        max_idx = np.argmax(probs)
        
        intent = self.encoder.inverse_transform([max_idx])[0]
        confidence = probs[max_idx]
        
        return intent, float(confidence)

    def predict_mood(self, text):
        """
        Predict the mood of the text using a Hybrid Approach.
        
        Layer 1: Keyword/Regex Matching (Fast, High Precision)
        Layer 2: Zero-Shot Cosine Similarity (Fallback, Contextual)
        
        Args:
            text (str): Input text
            
        Returns:
            str: Detected mood (Neutral, Angry, Happy, Confused, Urgent)
        """
        text_lower = text.lower()
        
        # --- LAYER 1: KEYWORD MATCHING ---
        keywords = {
            "Angry": [
                # Direct Anger
                "angry", "upset", "frustrated", "annoyed", "furious", "mad", "disappointed",
                # Service/Product Failures
                "worst", "terrible", "horrible", "awful", "garbage", "trash", "useless", "broken", "damaged", "defective",
                # Scams/Money
                "scam", "fraud", "rip off", "refund", "money back", "chargeback", "cheated",
                # Insults/Strong Language
                "stupid", "idiot", "incompetent", "ridiculous", "pathetic", "damn", "hell", "sucks"
            ],
            "Happy": [
                # Gratitude
                "thanks", "thank you", "thx", "appreciate", "grateful",
                # Positive Feedback
                "love", "great", "awesome", "amazing", "excellent", "perfect", "wonderful", "fantastic",
                "good job", "best", "satisfied", "happy", "fast shipping", "high quality"
            ],
            "Urgent": [
                # Time Sensitive
                "asap", "urgent", "emergency", "immediately", "right now", "hurry", "rush",
                "deadline", "late", "overdue", "where is my", "haven't received", "waiting"
            ],
            "Confused": [
                # Lack of Understanding
                "confused", "don't understand", "didn't understand", "unsure", "not sure", "clarify", "explain",
                # Weird Situations
                "weird", "strange", "odd", "doesn't make sense", "help me understand", "how do i", "what does this mean"
            ]
        }
        
        for mood, words in keywords.items():
            if any(word in text_lower for word in words):
                return mood
                
        # --- LAYER 2: SEMANTIC SIMILARITY (Zero-Shot) ---
        # If no strong keywords, compare embedding to mood anchors
        if self.embedder and hasattr(self, 'mood_anchors'):
            # Encode input
            input_vec = self.embedder.encode([text])[0]
            
            # Calculate similarity
            best_mood = "Neutral"
            highest_score = -1.0
            
            for mood, anchor_vec in self.mood_anchors.items():
                score = cosine_similarity([input_vec], [anchor_vec])[0][0]
                if score > highest_score:
                    highest_score = score
                    best_mood = mood
            
            # Threshold for non-neutral moods (prevent false positives)
            if best_mood != "Neutral" and highest_score < 0.35:
                return "Neutral"
                
            return best_mood
            
        return "Neutral"

