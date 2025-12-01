"""
Flow Manager Module for JUNO Automation Engine.
The central conductor that orchestrates the entire conversation flow.
Integrates FAQ, Intent Classification, Ticket Management, and Response Generation.
"""

import os
from src.m02_intent_classifier import IntentClassifier
from src.m03_faq_engine import FAQEngine
from src.m04_ticket_manager import TicketManager
from src.m07_jinja_email import TemplateEngine
from src.m06_email_state_manager import StateManager
from src.m05_entity_extractor import EntityExtractor
from src.m01_data_loader import DataLoader

class FlowManager:
    """
    Orchestrates the conversation flow:
    1. FAQ Check
    2. Intent Classification
    3. Ticket Management (Slot-Filling)
    4. Action Execution
    5. Response Generation
    """
    def __init__(self, project_root="."):
        print("🚀 Initializing JUNO Flow Manager...")
        
        # 1. Load Configs
        self.intent_config, self.mock_db, _ = DataLoader.load_configs(project_root)
        
        # 2. Initialize Components
        model_dir = os.path.join(project_root, "models")
        kb_path = os.path.join(project_root, "config", "knowledge_base.json")
        
        self.classifier = IntentClassifier(model_dir)
        self.faq_engine = FAQEngine(kb_path)
        self.ticket_manager = TicketManager(os.path.join(project_root, "jinja_emails", "tickets.json"))
        self.template_engine = TemplateEngine(os.path.join(project_root, "jinja_emails"))
        self.state_manager = StateManager(self.mock_db, self.intent_config)
        
        print("✅ Flow Manager Ready.")

    def process_email(self, user_id, text):
        """
        Process an incoming email and generate a response.
        
        Args:
            user_id (str): Unique identifier for the user (email address)
            text (str): The content of the email
            
        Returns:
            str: The generated response text
        """
        print(f"\n📨 Processing Email from {user_id}: '{text}'")
        
        # --- STEP 1: FAQ CHECK (The Fast Lane) ---
        # Only check FAQ if there is no active ticket (or if the user asks something totally new)
        # For simplicity, we check FAQ first. If high confidence, we answer.
        faq_match = self.faq_engine.get_best_match(text, threshold=0.60) # High threshold for auto-reply
        if faq_match:
            print(f"   ✅ FAQ Match Found: {faq_match['id']}")
            # We can wrap this in a template too if we want, but raw text is fine for now
            # Or use a generic 'faq_reply.j2'
            return faq_match['answer']

        # --- STEP 2: TICKET & INTENT MANAGEMENT ---
        ticket = self.ticket_manager.get_ticket(user_id)
        
        if ticket:
            print(f"   🎫 Active Ticket Found: {ticket.ticket_id} ({ticket.status})")
            # Update Ticket with new text (history)
            ticket.add_message("user", text)
            
            # If ticket is already resolved, we might be starting a new one? 
            # For now, assume if it's in DB, it's active.
            
            # Re-evaluate Mood on every turn
            mood = self.classifier.predict_mood(text)
            ticket.mood = mood # Update mood
            
        else:
            print("   🆕 No Active Ticket. Classifying Intent...")
            # Classify Intent
            intent, confidence = self.classifier.predict(text)
            mood = self.classifier.predict_mood(text)
            
            print(f"   🧠 Intent: {intent} ({confidence:.2f}) | Mood: {mood}")
            
            # Check Config for Requirements
            config = self.intent_config.get(intent)
            if not config:
                return "I'm sorry, I didn't understand that request. Could you rephrase?"
                
            required_entities = config.get("required_entities", [])
            
            # Create Ticket
            ticket = self.ticket_manager.create_ticket(
                user_id=user_id,
                intent=intent,
                mood=mood,
                entities={},
                missing_fields=required_entities
            )
            ticket.add_message("user", text)

        # --- STEP 3: ENTITY EXTRACTION & SLOT FILLING ---
        # Try to extract missing fields from the current text
        if ticket.missing_fields:
            print(f"   🔍 Looking for missing fields: {ticket.missing_fields}")
            # We only look for what is missing to avoid overwriting good data with bad guesses
            # But EntityExtractor.run_extraction takes a list.
            
            # Note: We pass the WHOLE text.
            extracted = EntityExtractor.run_extraction(
                text, 
                ticket.missing_fields, 
                self.mock_db # Needed for product lookup
            )
            
            if extracted:
                print(f"   ✨ Extracted: {extracted}")
                ticket.update_entities(extracted)
                self.ticket_manager.update_ticket(ticket)

        # --- STEP 4: DECISION & RESPONSE ---
        
        # Context for Templates
        context = {
            "user_name": user_id.split('@')[0].title(), # Simple name guess
            "mood": ticket.mood,
            "data": ticket.extracted_entities,
            "missing_fields": ticket.missing_fields
        }

        if ticket.is_complete():
            print("   ✅ Ticket Complete. Executing Action...")
            # Execute Action via StateManager
            action_result = self.state_manager.process_request(ticket.intent, ticket.extracted_entities)
            
            # Update Context with Action Result
            context["state"] = action_result["state"]
            context["data"].update(action_result["data"]) # Merge result data (e.g. status, tracking)
            
            # Select Template based on Intent
            # We need a mapping or convention. 
            # Convention: 'email_{intent}.j2' ? Or just hardcode for now.
            template_name = "email_base.j2" # Fallback
            
            if ticket.intent == "order_status":
                template_name = "email_order_status.j2"
            # Add more mappings here as we add templates
            
            response = self.template_engine.render(template_name, context)
            
            # Close Ticket if successful (or keep open if follow-up needed? For now, close)
            if action_result["state"] == "success":
                ticket.status = "RESOLVED"
                self.ticket_manager.close_ticket(user_id)
            else:
                # If not found, we might keep it open or close it. 
                # Let's close it for now as the user needs to provide new info (new ticket).
                ticket.status = "RESOLVED" 
                self.ticket_manager.close_ticket(user_id)
                
        else:
            print("   Warning: Ticket Incomplete. Requesting Info...")
            # Ticket still missing info
            ticket.status = "PENDING_CUSTOMER"
            self.ticket_manager.update_ticket(ticket)
            
            response = self.template_engine.render("email_request_info.j2", context)

        # Log Bot Response
        ticket.add_message("bot", response)
        
        return response

if __name__ == "__main__":
    # Test Logic
    manager = FlowManager()
    
    # Scenario 1: FAQ
    print("\n--- TEST 1: FAQ ---")
    print(manager.process_email("alice@example.com", "What is your return policy?"))
    
    # Scenario 2: Order Status (Missing Info)
    print("\n--- TEST 2: Order Status (Start) ---")
    print(manager.process_email("bob@example.com", "Where is my order? I am worried."))
    
    # Scenario 3: Order Status (Reply)
    print("\n--- TEST 3: Order Status (Reply) ---")
    print(manager.process_email("bob@example.com", "It is order #1001."))
