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
from setfit import SetFitModel
import torch


class IntentClassifier:
    """Wraps the Machine Learning Model for prediction."""
    
    def __init__(self, model_dir):
        """
        Initialize the intent classifier by loading the trained model.
        
        Args:
            model_dir (str): Directory containing the model files
        """
        print(f"⏳ Loading models from {model_dir}...")
        
        # Paths
        self.intent_model_path = os.path.join(model_dir, "intent_model", "mood_classifier.joblib") # Renamed folder
        self.label_encoder_path = os.path.join(model_dir, "intent_model", "mood_label_encoder.joblib")
        self.setfit_model_path = os.path.join(model_dir, "mood_model") # Renamed folder
        
        try:
            if not os.path.exists(self.intent_model_path) or not os.path.exists(self.label_encoder_path):
                raise FileNotFoundError(
                    f"Missing model files. Expected 'mood_classifier.joblib' and "
                    f"'mood_label_encoder.joblib' in {os.path.join(model_dir, 'intent_model')}"
                )
            
            # self.classifier = joblib.load(self.intent_model_path) # Removed RF
            # self.encoder = joblib.load(self.label_encoder_path) # Removed RF
            
            # Load Mood Model (SetFit)
            mood_model_path = self.setfit_model_path
            
            if os.path.exists(mood_model_path):
                try:
                    self.mood_classifier = SetFitModel.from_pretrained(mood_model_path)
                    print("✅ Mood Model (SetFit) Loaded.")
                except Exception as e:
                    print(f"⚠️ Failed to load SetFit model: {e}")
                    self.mood_classifier = None
            else:
                print("⚠️ Mood model not found at v2_setfit. Using fallback.")
                self.mood_classifier = None
            
            # Using the efficient MiniLM model (matches training)
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            # --- ZERO-SHOT INTENT ANCHORS ---
            # Map intents to representative phrases
            self.intent_map = {
                "order_status_inquiry": "Where is my order? Check order status. Tracking number.",
                "inventory_stock_availability": "Is this item in stock? Do you have this product?",
                "product_information_question": "Tell me about this product. What are the features?",
                "account_password_reset": "I forgot my password. Reset my account access.",
                "general_faq_question": "What is your return policy? How much is shipping?"
            }
            
            # Pre-compute embeddings for intents
            print("🧠 Computing Intent Embeddings...")
            self.intent_embeddings = {}
            for intent, phrase in self.intent_map.items():
                self.intent_embeddings[intent] = self.embedder.encode(phrase)
            
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
            self.embedder = None

    def predict(self, text):
        """
        Predict the intent of the given text using Zero-Shot Cosine Similarity.
        """
        if not self.embedder:
            return "error", 0.0
        
        # Encode input text
        text_embedding = self.embedder.encode(text)
        
        # Find best match
        best_intent = "unknown"
        best_score = -1.0
        
        for intent, anchor_embedding in self.intent_embeddings.items():
            # Cosine Similarity
            score = cosine_similarity([text_embedding], [anchor_embedding])[0][0]
            
            if score > best_score:
                best_score = score
                best_intent = intent
                
        # Threshold for "unknown"
        if best_score < 0.25: # Low threshold for now
            return "unknown", float(best_score)
            
        return best_intent, float(best_score)

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

        # --- LAYER 1: ML MODEL (SetFit) ---
        if self.mood_classifier:
            try:
                # Predict probabilities
                # SetFit predict_proba returns a tensor/array
                probs = self.mood_classifier.predict_proba([text])[0]
                
                # Get max probability and index
                if isinstance(probs, torch.Tensor):
                    probs = probs.cpu().detach().numpy()
                
                max_idx = np.argmax(probs)
                confidence = float(probs[max_idx])
                
                # Get label (SetFit models usually store labels in the config or we assume standard order)
                # If the model was saved correctly, it might have labels. 
                # Otherwise, we need to know the order. 
                # For now, let's try to infer or use a fixed list if we know it.
                # BUT, SetFitModel usually doesn't expose .classes_ directly like sklearn.
                # It relies on the underlying model head.
                # Let's assume the labels are sorted alphabetically or stored.
                # Actually, predict([text]) returns the label string directly!
                # But we want confidence.
                
                # Alternative: Use .predict() to get the label, and trust it if confidence is high?
                # But .predict() doesn't give confidence.
                
                # Let's try to get labels from the model config if possible.
                # self.mood_classifier.labels is often available in newer versions.
                labels = getattr(self.mood_classifier, "labels", None)
                
                if labels:
                    mood = labels[max_idx]
                else:
                    # Fallback: We know our 5 classes. They are usually sorted alphabetically by LabelEncoder during training.
                    # Angry, Confused, Happy, Neutral, Urgent
                    known_labels = ["Angry", "Confused", "Happy", "Neutral", "Urgent"]
                    mood = known_labels[max_idx]

                # Confidence Threshold (0.50 for SetFit)
                if confidence >= 0.50:
                    # --- SAFETY OVERRIDES (Fixing Model Bias) ---
                    text_lower = text.lower()
                    
                    # 1. False Happy (e.g. "I am not happy")
                    if mood == "Happy":
                        negatives = ["not happy", "unhappy", "disappointed", "delay", "waiting", "where is", "late"]
                        if any(n in text_lower for n in negatives):
                            print(f"🛡️ Safety Override: Happy -> Angry (Found '{[n for n in negatives if n in text_lower][0]}')")
                            return "Angry"

                    # 2. False Urgent (e.g. "Just checking status")
                    if mood == "Urgent":
                        calm_words = ["just checking", "curious", "wondering", "no rush", "take your time", "update?"]
                        if any(c in text_lower for c in calm_words):
                             print(f"🛡️ Safety Override: Urgent -> Neutral (Found '{[c for c in calm_words if c in text_lower][0]}')")
                             return "Neutral"

                    return mood
                    
            except Exception as e:
                print(f"⚠️ Mood Model Error: {e}")

        # --- LAYER 2: KEYWORD MATCHING (Fallback) ---
        return self._keyword_fallback(text)

    def _keyword_fallback(self, text):
        """Fallback to keyword matching."""
        text_lower = text.lower()
        keywords = {
            "Angry": [
                "angry", "upset", "frustrated", "annoyed", "furious", "mad", "disappointed",
                "worst", "terrible", "horrible", "awful", "garbage", "trash", "useless", "broken", "damaged", "defective",
                "scam", "fraud", "rip off", "refund", "money back", "chargeback", "cheated",
                "stupid", "idiot", "incompetent", "ridiculous", "pathetic", "damn", "hell", "sucks"
            ],
            "Happy": [
                "thanks", "thank you", "thx", "appreciate", "grateful",
                "love", "great", "awesome", "amazing", "excellent", "perfect", "wonderful", "fantastic",
                "good job", "best", "satisfied", "happy", "fast shipping", "high quality"
            ],
            "Urgent": [
                "asap", "urgent", "emergency", "immediately", "right now", "hurry", "rush",
                "deadline", "late", "overdue", "where is my", "haven't received", "waiting"
            ],
            "Confused": [
                "confused", "don't understand", "didn't understand", "unsure", "not sure", "clarify", "explain",
                "weird", "strange", "odd", "doesn't make sense", "help me understand", "how do i", "what does this mean"
            ]
        }
        
        # Special handling for negations
        if "not happy" in text_lower or "unhappy" in text_lower:
            return "Angry"
            
        for mood, words in keywords.items():
            if any(word in text_lower for word in words):
                return mood
                
        return "Neutral"

