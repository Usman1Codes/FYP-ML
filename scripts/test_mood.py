import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.m02_intent_classifier import IntentClassifier

# Config
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")

def run_tests():
    print("⏳ Initializing IntentClassifier...")
    try:
        classifier = IntentClassifier(MODEL_DIR)
    except Exception as e:
        print(f"❌ Failed to initialize classifier: {e}")
        return

    test_cases = [
        ("I am absolutely furious with your service!", "Angry"),
        ("Thank you so much, this is great.", "Happy"),
        ("I don't understand how to use this feature.", "Confused"),
        ("Where is my order? It's been 3 weeks!", "Urgent"),
        ("Just checking the status of ticket #123.", "Neutral"),
        # Hard Negatives
        ("I am not happy with the delay.", "Angry"), # "not happy" -> Angry
        ("I am happy to wait, no rush.", "Happy"),   # "happy" + "wait" -> Happy
        ("This is not urgent, take your time.", "Neutral"), # "not urgent" -> Neutral
        ("As per my last email, I am still waiting.", "Angry"), # Passive Aggressive
        ("Wow, great job breaking my order.", "Angry") # Sarcastic
    ]

    print("\n🧪 Running Mood Tests...")
    print(f"{'Text':<50} | {'Expected':<10} | {'Predicted':<10}")
    print("-" * 80)

    correct = 0
    for text, expected in test_cases:
        pred = classifier.predict_mood(text)
        
        # Check if prediction matches expected
        is_correct = pred == expected
        if is_correct:
            correct += 1
            icon = "✅"
        else:
            icon = "❌"
            
        print(f"{text[:47]:<50} | {expected:<10} | {pred:<10} {icon}")

    print("-" * 80)
    print(f"🎯 Accuracy: {correct}/{len(test_cases)} ({correct/len(test_cases)*100:.1f}%)")

if __name__ == "__main__":
    run_tests()
