import os
import json
import re
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

# =============================================================================
# SECTION 0: GLOBAL CONFIGURATION & SETUP
# =============================================================================

PROJECT_ROOT = "."

# EXACT filenames based on your directory structure
PATHS = {
    "intent_config": os.path.join(PROJECT_ROOT, "Intent-Templates/intent-variable.json"),
    "mock_db": os.path.join(PROJECT_ROOT, "Intent-Templates/mock-database.json"),
    "templates": os.path.join(PROJECT_ROOT, "Intent-Templates/reponse-templates.json"),
    "model_dir": os.path.join(PROJECT_ROOT, "models")
}

print("--- JUNO ENGINE INITIALIZING ---")

# =============================================================================
# SECTION 1: INFRASTRUCTURE (DATA LOADERS)
# =============================================================================

class DataLoader:
    """Handles loading JSON configurations and Databases."""
    
    @staticmethod
    def load_json(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ CRITICAL ERROR: Could not find {filepath}")
            return {}
        except json.JSONDecodeError:
            print(f"❌ CRITICAL ERROR: Invalid JSON in {filepath}")
            return {}

# Load configs
INTENT_CONFIG = DataLoader.load_json(PATHS["intent_config"])
MOCK_DB = DataLoader.load_json(PATHS["mock_db"])
TEMPLATES = DataLoader.load_json(PATHS["templates"])

if not INTENT_CONFIG:
    print("⚠️ WARNING: Intent Config is empty. Check 'config/intent-variable.json'")
else:
    print("✅ Configuration & Database Loaded.")


# =============================================================================
# SECTION 2: INTENT INFERENCE ENGINE (The Classifier)
# =============================================================================

class IntentEngine:
    """Wraps the Machine Learning Model for prediction."""
    
    def __init__(self, model_dir):
        print(f"⏳ Loading models from {model_dir}...")
        
        # EXACT FILENAMES (Updated for your PC)
        model_path = os.path.join(model_dir, "intent_classifier.joblib")
        encoder_path = os.path.join(model_dir, "label_encoder.joblib")
        
        try:
            if not os.path.exists(model_path) or not os.path.exists(encoder_path):
                raise FileNotFoundError(f"Missing model files. Expected 'intent_classifier.joblib' in {model_dir}")
            
            self.classifier = joblib.load(model_path)
            self.encoder = joblib.load(encoder_path)
            
            # Using the efficient MiniLM model (matches your training)
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            
            print(f"✅ AI Engine Ready.")
            
        except Exception as e:
            print(f"❌ AI Engine Failed: {e}")
            self.classifier = None

    def predict(self, text):
        if not self.classifier: return "error", 0.0
        
        # Preprocess
        clean_text = re.sub(r'\s+', ' ', text).strip()
        
        # Vectorize & Predict
        vector = self.embedder.encode([clean_text])
        probs = self.classifier.predict_proba(vector)[0]
        max_idx = np.argmax(probs)
        
        intent = self.encoder.inverse_transform([max_idx])[0]
        confidence = probs[max_idx]
        
        return intent, float(confidence)

# Initialize Engine
ai_engine = IntentEngine(PATHS["model_dir"])


# =============================================================================
# SECTION 3: ENTITY EXTRACTOR (The Miner)
# =============================================================================

# =============================================================================
# SECTION 3: ENTITY EXTRACTOR (The Miner) - IMPROVED
# =============================================================================

class EntityExtractor:
    """
    Extracts structured data (Order IDs, Emails, Products) from text.
    Uses Strict Regex + Knowledge Base lookup to avoid false positives.
    """
    
    @staticmethod
    def extract_order_id(text):
        """
        Robust Logic:
        1. Must be 5+ characters long.
        2. MUST contain at least one DIGIT (0-9). This prevents matching words like "Where".
        3. Supports formats: #12345, ORD-459, 123456, Order 999
        """
        # Pattern Breakdown:
        # \b              -> Start at a word boundary
        # (?:#|Order...)? -> Optional Prefix (like #, Order, ID)
        # (               -> Start Capture Group
        #   [A-Z0-9-]* -> Any letters/numbers
        #   \d            -> MUST HAVE AT LEAST ONE DIGIT
        #   [A-Z0-9-]* -> Any letters/numbers
        # )               -> End Capture Group
        # {5,}            -> The capture group must be at least 5 chars long
        
        # We use a two-step regex for clarity. 
        
        # Step 1: Look for explicit labeled IDs (High Confidence)
        # Matches: #12345, Order: 12345, Ref 12345
        explicit_pattern = r'(?:#|Order\s*:?\s*|id\s*:?\s*|ref\s*:?\s*)([A-Z0-9-]{5,})'
        match = re.search(explicit_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

        # Step 2: Look for standalone IDs (Medium Confidence)
        # Matches: 12345, ORD-123, 99999
        # Constraint: Must contain a digit to avoid English words.
        tokens = text.split()
        for token in tokens:
            # Clean punctuation from edges
            clean_token = token.strip(".,?!")
            
            # Check conditions: Length >= 5 AND contains digit AND allows A-Z, 0-9, -
            if len(clean_token) >= 5 and any(char.isdigit() for char in clean_token):
                # Verify it doesn't contain weird symbols (like emails)
                if re.match(r'^[A-Z0-9-]+$', clean_token, re.IGNORECASE):
                    return clean_token
                    
        return None

    @staticmethod
    def extract_email(text):
        # Standard email regex
        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    @staticmethod
    def extract_product(text, database):
        """
        Scans text for product names defined in mock-database.json.
        Uses word-boundary checks to prevent partial matches.
        """
        text_lower = " " + text.lower() + " " # Pad with spaces for boundary check
        
        for product in database.get("products", []):
            official_name = product["product_name"].lower()
            
            # Check official name
            if f" {official_name} " in text_lower or official_name in text.lower():
                return product["product_name"]
            
            # Check aliases (synonyms)
            for alias in product.get("aliases", []):
                alias_lower = alias.lower()
                # Check if alias exists in text (simple substring check usually works best for products)
                if alias_lower in text_lower:
                    return product["product_name"] # Normalize to official name
                    
        return None

    @staticmethod
    def run_extraction(text, required_entities):
        """
        Only looks for what is REQUIRED by the intent config.
        """
        extracted = {}
        
        if "order_id" in required_entities:
            extracted["order_id"] = EntityExtractor.extract_order_id(text)
            
        if "email" in required_entities:
            extracted["email"] = EntityExtractor.extract_email(text)
            
        if "product_name" in required_entities:
            extracted["product_name"] = EntityExtractor.extract_product(text, MOCK_DB)
            
        return extracted


# =============================================================================
# SECTION 4: STATE MANAGER (The Brain)
# =============================================================================

class StateManager:
    """
    Checks requirements and executes "Actions" (DB Lookups).
    """
    
    def __init__(self, db):
        self.db = db

    def process_request(self, intent, extracted_data):
        # 1. Get Rules from intent-variable.json
        config = INTENT_CONFIG.get(intent)
        if not config:
            return {"state": "error", "data": {}, "missing": []}

        # 2. Check Requirements
        required = config.get("required_entities", [])
        missing = [req for req in required if not extracted_data.get(req)]
        
        # STATE A: MISSING INFO
        if missing:
            return {"state": "missing_info", "data": {}, "missing": missing}

        # 3. Execute Action (Dispatch)
        action = config.get("action_type")
        
        if action == "lookup_order":
            return self._lookup_order(extracted_data["order_id"])
            
        elif action == "check_stock":
            return self._check_stock(extracted_data["product_name"])
            
        elif action == "get_product_info":
            return self._get_product_info(extracted_data["product_name"])
            
        elif action == "trigger_reset":
            return self._trigger_reset(extracted_data["email"])
            
        elif action == "general_reply":
            return {"state": "success", "data": {}}

        return {"state": "error", "data": {}}

    # --- INTERNAL ACTION HANDLERS ---
    
    def _lookup_order(self, order_id):
        orders = self.db.get("orders", [])
        result = next((item for item in orders if item["order_id"] == order_id), None)
        
        if result:
            return {"state": "success", "data": result}
        else:
            return {"state": "not_found", "data": {"order_id": order_id}}

    def _check_stock(self, product_name):
        products = self.db.get("products", [])
        result = next((item for item in products if item["product_name"] == product_name), None)
        
        if result:
            return {"state": "success", "data": result}
        else:
            return {"state": "not_found", "data": {"product_name": product_name}}

    def _get_product_info(self, product_name):
        return self._check_stock(product_name)

    def _trigger_reset(self, email):
        users = self.db.get("users", [])
        result = next((item for item in users if item["email"] == email), None)
        
        if result:
            return {"state": "success", "data": {"email": email}}
        else:
            return {"state": "not_found", "data": {"email": email}}


# =============================================================================
# SECTION 5: RESPONSE ENGINE (The Speaker)
# =============================================================================

class ResponseEngine:
    """Fills the templates from reponse-templates.json."""
    
    @staticmethod
    def generate_response(intent, state_result):
        # 1. Get Template Group
        templates = TEMPLATES.get(intent, {})
        
        state = state_result["state"]
        data = state_result.get("data", {})
        
        # 2. Select Template
        if state == "missing_info":
            return templates.get("missing_info", "Could you provide more details?")
            
        elif state == "not_found":
            raw_text = templates.get("not_found", "Record not found.")
            return raw_text.format(**data)
            
        elif state == "success":
            raw_text = templates.get("success", "Request processed.")
            try:
                return raw_text.format(**data)
            except KeyError as e:
                return f"System Error: Missing data field {e}"
        
        return "I'm sorry, I encountered a system error processing your request."


# =============================================================================
# SECTION 6: MAIN PIPELINE & TESTING
# =============================================================================

def process_incoming_email(email_text):
    print(f"\n📨 NEW MESSAGE: '{email_text}'")
    
    # 1. CLASSIFY
    intent, confidence = ai_engine.predict(email_text)
    print(f"   🧠 Intent: {intent} ({confidence:.2f})")
    
    # High confidence threshold
    if confidence < 0.65:
        print("   ⚠️ Low Confidence.")
        return "I'm not quite sure how to help with that. Could you rephrase?"

    # 2. CONFIG LOOKUP
    intent_rules = INTENT_CONFIG.get(intent)
    if not intent_rules:
        print(f"   ❌ Config missing for intent: {intent}")
        return "System configuration error."

    required_entities = intent_rules.get("required_entities", [])
    
    # 3. EXTRACT
    extracted_data = EntityExtractor.run_extraction(email_text, required_entities)
    print(f"   ⛏️  Extracted: {extracted_data}")
    
    # 4. MANAGE STATE
    manager = StateManager(MOCK_DB)
    result = manager.process_request(intent, extracted_data)
    print(f"   ⚙️  State: {result['state']}")
    
    # 5. RESPOND
    final_reply = ResponseEngine.generate_response(intent, result)
    print(f"   🤖 REPLY: \"{final_reply}\"")
    
    return final_reply

if __name__ == "__main__":
    # --- TEST CASES ---
    process_incoming_email("Where is my order #12345?")
    process_incoming_email("I'm worried about my shipment. Has it left yet?")
    process_incoming_email("Do you have the navy jacket in stock?")
    process_incoming_email("I forgot my password for john@example.com")