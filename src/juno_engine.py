"""
JUNO Automation Engine - Main Entry Point

A robust, hybrid AI engine for automated customer support. It combines 
Machine Learning for intent classification with a deterministic rule-based 
engine for safe, accurate data retrieval.
"""

import os
import sys

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_loader import DataLoader
from src.intent_classifier import IntentClassifier
from src.entity_extractor import EntityExtractor
from src.state_manager import StateManager
from src.response_engine import ResponseEngine


# =============================================================================
# GLOBAL CONFIGURATION & SETUP
# =============================================================================

# Get project root (parent of src directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths based on new directory structure
PATHS = {
    "config_dir": os.path.join(PROJECT_ROOT, "config"),
    "model_dir": os.path.join(PROJECT_ROOT, "models")
}

print("--- JUNO ENGINE INITIALIZING ---")

# Load configurations
INTENT_CONFIG, MOCK_DB, TEMPLATES = DataLoader.load_configs(PROJECT_ROOT)

# Initialize AI Engine
ai_engine = IntentClassifier(PATHS["model_dir"])


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def process_incoming_email(email_text):
    """
    Process an incoming email through the complete JUNO pipeline.
    
    Pipeline:
    1. Classify intent using ML model
    2. Look up intent configuration
    3. Extract required entities
    4. Manage state and execute actions
    5. Generate and return response
    
    Args:
        email_text (str): The customer email text to process
        
    Returns:
        str: Generated response text
    """
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
    extracted_data = EntityExtractor.run_extraction(
        email_text, 
        required_entities, 
        database=MOCK_DB
    )
    print(f"   ⛏️  Extracted: {extracted_data}")
    
    # 4. MANAGE STATE
    manager = StateManager(MOCK_DB, INTENT_CONFIG)
    result = manager.process_request(intent, extracted_data)
    print(f"   ⚙️  State: {result['state']}")
    
    # 5. RESPOND
    final_reply = ResponseEngine.generate_response(intent, result, TEMPLATES)
    print(f"   🤖 REPLY: \"{final_reply}\"")
    
    return final_reply


if __name__ == "__main__":
    # --- TEST CASES ---
    process_incoming_email("Where is my order #12345?")
    process_incoming_email("I'm worried about my shipment. Has it left yet?")
    process_incoming_email("Do you have the navy jacket in stock?")
    process_incoming_email("I forgot my password for john@example.com")

