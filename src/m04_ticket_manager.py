"""
Ticket Management Module for JUNO Automation Engine.
Handles the creation, retrieval, and updating of conversation state (Tickets).
"""

import uuid
import time
import json
import os
from datetime import datetime

class Ticket:
    """
    Represents a single customer support interaction state.
    """
    def __init__(self, user_id, intent, mood="Neutral", entities=None, missing_fields=None, severity="Low"):
        self.ticket_id = str(uuid.uuid4())
        self.user_id = user_id
        self.intent = intent
        self.mood = mood
        self.severity = severity
        self.extracted_entities = entities or {}
        self.missing_fields = missing_fields or []
        self.status = "OPEN" # OPEN, PENDING_CUSTOMER, RESOLVED
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.history = [] # List of message dicts

    def update_entities(self, new_entities):
        """Update extracted entities and remove them from missing fields."""
        if not new_entities:
            return

        # Only update if value is not None
        valid_updates = {k: v for k, v in new_entities.items() if v is not None}
        if not valid_updates:
            return

        self.extracted_entities.update(valid_updates)
        
        # Remove found entities from missing list
        if self.missing_fields:
            self.missing_fields = [
                field for field in self.missing_fields 
                if field not in self.extracted_entities
            ]
            
        self.updated_at = datetime.now().isoformat()

    def add_message(self, sender, text):
        """Add a message to the ticket history."""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "sender": sender, # 'user' or 'bot'
            "text": text
        })

    def is_complete(self):
        """Check if all required fields are present."""
        return len(self.missing_fields) == 0

    def to_dict(self):
        """Serialize ticket to dictionary."""
        return {
            "ticket_id": self.ticket_id,
            "user_id": self.user_id,
            "intent": self.intent,
            "mood": self.mood,
            "severity": self.severity,
            "extracted_entities": self.extracted_entities,
            "missing_fields": self.missing_fields,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data):
        """Create Ticket instance from dictionary."""
        ticket = cls(
            user_id=data["user_id"],
            intent=data["intent"],
            mood=data.get("mood", "Neutral"),
            severity=data.get("severity", "Low"),
            entities=data.get("extracted_entities"),
            missing_fields=data.get("missing_fields")
        )
        ticket.ticket_id = data["ticket_id"]
        ticket.status = data["status"]
        ticket.created_at = data["created_at"]
        ticket.updated_at = data["updated_at"]
        ticket.history = data.get("history", [])
        return ticket


class TicketManager:
    """
    Manages the storage and retrieval of Tickets.
    Uses JSON file storage for persistence.
    """
    def __init__(self, storage_file="jinja_emails/tickets.json"):
        self.storage_file = storage_file
        self.tickets = self._load_tickets()

    def _load_tickets(self):
        """Load tickets from JSON file."""
        if not os.path.exists(self.storage_file):
            return {}
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                # Convert dicts back to Ticket objects
                return {
                    user_id: Ticket.from_dict(ticket_data)
                    for user_id, ticket_data in data.items()
                }
        except Exception as e:
            print(f"⚠️ Failed to load tickets: {e}")
            return {}

    def _save_tickets(self):
        """Save tickets to JSON file."""
        try:
            data = {
                user_id: ticket.to_dict()
                for user_id, ticket in self.tickets.items()
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save tickets: {e}")

    def calculate_severity(self, mood):
        """Calculate ticket severity based on mood."""
        if mood in ["Angry", "Urgent"]:
            return "High"
        elif mood == "Confused":
            return "Medium"
        return "Low"

    def create_ticket(self, user_id, intent, mood, entities, missing_fields, severity=None):
        """Create and store a new ticket."""
        if severity is None:
            severity = self.calculate_severity(mood)
            
        ticket = Ticket(user_id, intent, mood, entities, missing_fields, severity)
        self.tickets[user_id] = ticket
        self._save_tickets() # Persist immediately
        print(f"🎫 Ticket Created: {ticket.ticket_id} for User: {user_id}")
        return ticket

    def get_ticket(self, user_id):
        """Get the active ticket for a user."""
        return self.tickets.get(user_id)

    def update_ticket(self, ticket):
        """
        Explicitly save updates to a ticket.
        Call this after modifying a ticket object.
        """
        self.tickets[ticket.user_id] = ticket
        self._save_tickets()

    def close_ticket(self, user_id):
        """Remove a ticket (mark as resolved/closed)."""
        if user_id in self.tickets:
            del self.tickets[user_id]
            self._save_tickets()
            print(f"🎫 Ticket Closed for User: {user_id}")

if __name__ == "__main__":
    # Test Logic
    print("--- Testing Ticket Manager (Persistence) ---")
    manager = TicketManager("test_tickets.json")
    
    # 1. Create
    print("\n1. Creating Ticket...")
    t = manager.create_ticket(
        "john@example.com", 
        "order_status", 
        "Neutral", 
        {}, 
        ["order_id"],
        severity="Low"
    )
    print(f"   Status: {t.status}, Severity: {t.severity}, Missing: {t.missing_fields}")
    
    # 2. Update
    print("\n2. Updating Ticket...")
    t.update_entities({"order_id": "12345"})
    manager.update_ticket(t) # Save changes
    print(f"   Updated Missing: {t.missing_fields}")
    
    # 3. Reload
    print("\n3. Reloading Manager (Simulating Restart)...")
    new_manager = TicketManager("test_tickets.json")
    loaded_t = new_manager.get_ticket("john@example.com")
    
    if loaded_t:
        print(f"   ✅ Loaded Ticket ID: {loaded_t.ticket_id}")
        print(f"   ✅ Data: {loaded_t.extracted_entities}")
    else:
        print("   ❌ Failed to load ticket.")
        
    # Cleanup
    if os.path.exists("test_tickets.json"):
        os.remove("test_tickets.json")
