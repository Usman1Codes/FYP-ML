"""
Train Mood Classifier (Random Forest)
"""
import os
import json
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sentence_transformers import SentenceTransformer

# CONFIG
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "mood_training_data.json")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "mood_classifier.joblib")
ENCODER_PATH = os.path.join(MODEL_DIR, "mood_label_encoder.joblib")

def train():
    print("🚀 Starting Mood Model Training...")
    
    # 1. Load Data
    if not os.path.exists(DATA_FILE):
        print(f"❌ Error: Data file not found at {DATA_FILE}")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📚 Loaded {len(data)} examples.")
    
    texts = [item['text'] for item in data]
    labels = [item['mood'] for item in data]
    
    # 2. Embed Data
    print("🧠 Generating Embeddings (all-MiniLM-L6-v2)...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    X = embedder.encode(texts, show_progress_bar=True)
    
    # 3. Encode Labels
    le = LabelEncoder()
    y = le.fit_transform(labels)
    
    # 4. Split Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 5. Train Random Forest
    print("🌲 Training Random Forest...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # 6. Evaluate
    print("\n📊 Evaluation Results:")
    y_pred = clf.predict(X_test)
    print(classification_report(le.inverse_transform(y_test), le.inverse_transform(y_pred)))
    
    # 7. Save
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        
    joblib.dump(clf, MODEL_PATH)
    joblib.dump(le, ENCODER_PATH)
    print(f"✅ Model saved to {MODEL_PATH}")
    print(f"✅ Encoder saved to {ENCODER_PATH}")

if __name__ == "__main__":
    train()
