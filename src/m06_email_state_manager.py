"""
State management module for the JUNO Automation Engine.
Checks requirements and executes actions (database lookups).
"""


from src.m05_entity_extractor import EntityExtractor

class StateManager:
    """
    Checks requirements and executes "Actions" (DB Lookups).
    """
    
    def __init__(self, db, intent_config):
        """
        Initialize the state manager.
        
        Args:
            db (dict): Mock database containing orders, products, users
            intent_config (dict): Intent configuration dictionary
        """
        self.db = db
        self.intent_config = intent_config

    def process_request(self, intent, extracted_data):
        """
        Process a request by checking requirements and executing actions.
        
        Args:
            intent (str): The predicted intent
            extracted_data (dict): Extracted entities from the text
            
        Returns:
            dict: State result with 'state', 'data', and optionally 'missing' keys
        """
        # 1. Get Rules from intent_config
        config = self.intent_config.get(intent)
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
        print(f"   [DEBUG-STATE] Intent: {intent}, Action: {action}, Extracted: {extracted_data}")
        
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
    
    def _validate_order_id(self, order_id):
        """Check if order ID format is valid."""
        # Allow: #12345, ORD-123, or just digits 12345
        if not order_id: return False
        if order_id.startswith("#") or order_id.upper().startswith("ORD-") or order_id.isdigit():
            return True
        # Also allow alphanumeric if it looks like a hash (e.g. 5 chars+)
        if len(order_id) >= 4 and any(c.isdigit() for c in order_id):
            return True
        return False

    def _lookup_order(self, order_id):
        """Look up an order in the database."""
        # EDGE CASE 2: Validation
        if not self._validate_order_id(order_id):
            return {"state": "invalid_format", "data": {}, "missing": ["Order ID"]}

        orders = self.db.get("orders", [])
        result = next((item for item in orders if item["order_id"] == order_id), None)
        
        if result:
            return {"state": "success", "data": result}
        else:
            return {"state": "not_found", "data": {"order_id": order_id}}

    def _check_stock(self, product_name):
        """Check stock status for a product."""
        products = self.db.get("products", [])
        result = next((item for item in products if item["product_name"] == product_name), None)
        
        if result:
            return {"state": "success", "data": result}
        else:
            return {"state": "not_found", "data": {"product_name": product_name}}

    def _get_product_info(self, product_name):
        """Get product information."""
        return self._check_stock(product_name)

    def _trigger_reset(self, email):
        """Trigger password reset for a user."""
        users = self.db.get("users", [])
        result = next((item for item in users if item["email"] == email), None)
        
        if result:
            return {"state": "success", "data": {"email": email}}
        else:
            return {"state": "not_found", "data": {"email": email}}

