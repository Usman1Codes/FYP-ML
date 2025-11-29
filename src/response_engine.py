"""
Response generation module for the JUNO Automation Engine.
Fills templates from response_templates.json to generate responses.
"""


class ResponseEngine:
    """Fills the templates from response_templates.json."""
    
    @staticmethod
    def generate_response(intent, state_result, templates):
        """
        Generate a response based on intent and state result.
        
        Args:
            intent (str): The predicted intent
            state_result (dict): State result from StateManager
            templates (dict): Response templates dictionary
            
        Returns:
            str: Generated response text
        """
        # 1. Get Template Group
        intent_templates = templates.get(intent, {})
        
        state = state_result["state"]
        data = state_result.get("data", {})
        
        # 2. Select Template
        if state == "missing_info":
            return intent_templates.get("missing_info", "Could you provide more details?")
            
        elif state == "not_found":
            raw_text = intent_templates.get("not_found", "Record not found.")
            return raw_text.format(**data)
            
        elif state == "success":
            raw_text = intent_templates.get("success", "Request processed.")
            try:
                return raw_text.format(**data)
            except KeyError as e:
                return f"System Error: Missing data field {e}"
        
        return "I'm sorry, I encountered a system error processing your request."

