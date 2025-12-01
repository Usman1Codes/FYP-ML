import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.m09_flow_manager import FlowManager

print("--- TESTING FLOW MANAGER ---")
manager = FlowManager()

# Scenario 1: FAQ
print("\n[Test 1] FAQ Check")
response = manager.process_email("alice@example.com", "What is your return policy?")
print(f"Response: {response[:50]}...")

# Scenario 2: Order Status (Missing Info)
print("\n[Test 2] Order Status (Start)")
# Ensure no previous ticket exists (for test purity)
if "bob@example.com" in manager.ticket_manager.tickets:
    manager.ticket_manager.close_ticket("bob@example.com")
    
response = manager.process_email("bob@example.com", "Where is my order? I am worried.")
print(f"Response: {response[:50]}...")

# Scenario 3: Order Status (Reply)
print("\n[Test 3] Order Status (Reply)")
response = manager.process_email("bob@example.com", "It is order #12345.")
print(f"Response: {response[:50]}...")
