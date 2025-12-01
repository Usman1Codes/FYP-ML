"""
JUNO Automation Engine - Main Entry Point

A robust, hybrid AI engine for automated customer support.
Integrates:
- FlowManager (Routing, Slot-Filling, Logic)
- ComplianceEngine (Safety & Tone Vetting)
"""

import os
import sys

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.m09_flow_manager import FlowManager
from src.m08_gemini_evaluation import ComplianceEngine

# =============================================================================
# GLOBAL CONFIGURATION & SETUP
# =============================================================================

print("--- JUNO ENGINE INITIALIZING ---")

# Initialize Core Engines
flow_manager = FlowManager(project_root)
compliance_engine = ComplianceEngine() # Will use env var or fail open

# =============================================================================
# MAIN PIPELINE
# =============================================================================

def process_incoming_email(user_id, email_text):
    """
    Process an incoming email through the complete JUNO pipeline.
    
    Pipeline:
    1. FlowManager: Handle FAQ, Intents, Tickets, Slot-Filling, Drafting.
    2. ComplianceEngine: Vet the draft for safety and tone.
    
    Args:
        user_id (str): Unique identifier for the user (email address)
        email_text (str): The customer email text to process
        
    Returns:
        str: Final vetted response text
    """
    print(f"\n📨 NEW MESSAGE from {user_id}: '{email_text}'")
    
    # 1. GENERATE DRAFT (Flow Manager)
    # This handles everything: FAQ, Tickets, Database, Templates
    draft_response = flow_manager.process_email(user_id, email_text)
    
    # Get current mood from ticket (if exists) for compliance context
    # We can peek into the ticket manager
    ticket = flow_manager.ticket_manager.get_ticket(user_id)
    current_mood = ticket.mood if ticket else "Neutral"
    
    print(f"   📝 Draft Generated (Mood: {current_mood})")
    
    # 2. VET RESPONSE (Compliance Layer)
    final_response = compliance_engine.vet_response(draft_response, mood=current_mood)
    
    if final_response != draft_response:
        print("   🛡️  Compliance Engine modified the response.")
    
    print(f"   🚀 SENT: \"{final_response[:50]}...\"")
    
    return final_response


if __name__ == "__main__":
    # --- TEST CASES ---
    
    # 1. FAQ
    process_incoming_email("alice@example.com", "What is your return policy?")
    
    # 2. Transaction (Happy Path)
    process_incoming_email("charlie@example.com", "Where is my order #12345?")
    
    # 3. Transaction (Slot Filling + Angry)
    process_incoming_email("dave@example.com", "I am furious! Where is my package?")
    process_incoming_email("dave@example.com", "It is #99999") # Not found scenario
