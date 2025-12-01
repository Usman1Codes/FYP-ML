"""
FAQ Engine Module for JUNO Automation Engine.
Handles semantic search against the Knowledge Base for General FAQ queries.
"""

import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class FAQEngine:
    """
    Handles semantic search for FAQ retrieval.
    """
    def __init__(self, config_path, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the FAQ Engine.
        
        Args:
            config_path (str): Path to knowledge_base.json
            model_name (str): Sentence Transformer model name
        """
        print(f"📚 Loading Knowledge Base from: {config_path}")
        self.kb = self._load_kb(config_path)
        
        print(f"🧠 Loading FAQ Model: {model_name}")
        self.embedder = SentenceTransformer(model_name)
        
        # Pre-compute embeddings for all questions
        self.questions = []
        self.question_map = [] # Maps index back to entry
        
        for entry in self.kb.get("faq_entries", []):
            for q in entry["questions"]:
                self.questions.append(q)
                self.question_map.append(entry)
                
        if self.questions:
            self.embeddings = self.embedder.encode(self.questions)
        else:
            self.embeddings = None
            print("⚠️ Warning: Knowledge Base is empty.")

    def _load_kb(self, path):
        """Load JSON knowledge base."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load KB: {e}")
            return {}

    def get_best_match(self, query, threshold=0.4):
        """
        Find the best matching FAQ answer.
        
        Args:
            query (str): User's question
            threshold (float): Minimum similarity score to return a match
            
        Returns:
            dict or None: Best matching entry (with 'answer') or None
        """
        if self.embeddings is None:
            return None
            
        query_vec = self.embedder.encode([query])
        scores = cosine_similarity(query_vec, self.embeddings)[0]
        
        best_idx = np.argmax(scores)
        best_score = scores[best_idx]
        
        print(f"   🔍 FAQ Match Score: {best_score:.2f} (Threshold: {threshold})")
        
        if best_score >= threshold:
            return self.question_map[best_idx]
            
        return None

if __name__ == "__main__":
    # Test Logic
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    kb_path = os.path.join(base_path, "config", "knowledge_base.json")
    
    engine = FAQEngine(kb_path)
    
    test_q = "I want to return my shoes."
    match = engine.get_best_match(test_q)
    
    if match:
        print(f"Q: {test_q}\nA: {match['answer']}")
    else:
        print("No match found.")
