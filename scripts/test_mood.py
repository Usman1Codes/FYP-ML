import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.m02_intent_classifier import IntentClassifier

# Initialize
# Note: We need the models directory. Assuming it exists at ../models
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
model_dir = os.path.join(project_root, 'models')

print(f"Initializing Classifier from {model_dir}...")
classifier = IntentClassifier(model_dir)

# Test Cases
test_sentences = [
    ("I am so angry with your service!", "Angry"), # Keyword 'angry'
    ("This is absolutely ridiculous.", "Angry"),   # Keyword 'ridiculous'
    ("I love this product, thanks!", "Happy"),     # Keyword 'love', 'thanks'
    ("Can you help me? I don't understand.", "Confused"), # Keyword 'don't understand'
    ("I need this immediately.", "Urgent"),        # Keyword 'immediately'
    ("The package was damaged and I am very upset.", "Angry"), # Contextual/Keyword
    ("Just checking my order status.", "Neutral"), # Neutral
    ("This is unacceptable behavior.", "Angry"),   # Semantic (Zero-Shot) - No strong keyword?
]

print("\n--- MOOD DETECTION TEST ---")
for text, expected in test_sentences:
    mood = classifier.predict_mood(text)
    print(f"Text: '{text}'\n  -> Predicted: {mood} | Expected: {expected}")
    if mood == expected:
        print("  ✅ PASS")
    else:
        print("  ⚠️ CHECK (Might be Semantic Layer)")
