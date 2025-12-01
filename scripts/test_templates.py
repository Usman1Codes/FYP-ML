import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.m07_jinja_email import TemplateEngine

print("--- TESTING TEMPLATE ENGINE ---")
engine = TemplateEngine()

# Test 1: Order Status (Success + Happy)
print("\n[Test 1] Order Status (Success + Happy)")
ctx1 = {
    "user_name": "Sarah",
    "mood": "Happy",
    "state": "success",
    "data": {
        "order_id": "12345",
        "status": "Shipped",
        "delivery_date": "Tomorrow",
        "tracking_link": "http://track.me/123"
    }
}
print(engine.render("email_order_status.j2", ctx1))

# Test 2: Order Status (Not Found + Angry)
print("\n[Test 2] Order Status (Not Found + Angry)")
ctx2 = {
    "user_name": "Mike",
    "mood": "Angry",
    "state": "not_found",
    "data": {"order_id": "99999"}
}
print(engine.render("email_order_status.j2", ctx2))

# Test 3: Request Info (Urgent)
print("\n[Test 3] Request Info (Urgent)")
ctx3 = {
    "user_name": "Dave",
    "mood": "Urgent",
    "missing_fields": ["order_id", "email_address"]
}
print(engine.render("email_request_info.j2", ctx3))
