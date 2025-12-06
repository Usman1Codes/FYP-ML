import os
from setfit import SetFitModel
import numpy as np

MODEL_PATH = "/home/muhammad-usman/FYP/ML/models/v2_setfit"

print(f"⏳ Loading model from {MODEL_PATH}...")
model = SetFitModel.from_pretrained(MODEL_PATH)

print("\n📋 Model Labels:")
if hasattr(model, "labels"):
    print(model.labels)
else:
    print("❌ model.labels not found!")

test_texts = [
    "I am absolutely furious",
    "Where is my order? It's been 3 weeks!",
    "Just checking the status of ticket #123.",
    "I am not happy with the delay.",
    "As per my last email, I am still waiting.",
    "Wow, great job breaking my order."
]

print("\n🔮 Predictions:")
for text in test_texts:
    # Predict Label directly
    pred_label = model.predict([text])[0]
    
    # Predict Proba
    probs = model.predict_proba([text])[0]
    max_idx = np.argmax(probs)
    
    print(f"Text: '{text}'")
    print(f"  -> .predict():       {pred_label}")
    print(f"  -> .predict_proba(): {probs}")
    print(f"  -> Max Index:        {max_idx}")
    if hasattr(model, "labels"):
        print(f"  -> Mapped Label:     {model.labels[max_idx]}")
    print("-" * 30)
