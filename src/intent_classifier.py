"""
Intent classification module for the JUNO Automation Engine.
Wraps the Machine Learning Model for intent prediction.
"""

import os
import re
import joblib
import numpy as np
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

