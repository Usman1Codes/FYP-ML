"""
Compliance Engine Module for JUNO Automation Engine.
Uses Google Gemini API to vet email drafts for safety, tone, and professionalism.
Acts as a final quality gate before sending.
"""

import os
import os
try:
    import google.generativeai as genai
    from google.api_core import exceptions
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    genai = None

class ComplianceEngine:
    """
    Vets email drafts using LLM (Gemini) to ensure they are safe, 
    professional, and empathetic.
    """
    def __init__(self, api_key=None):
        """
        Initialize the Compliance Engine.
        
        Args:
            api_key (str): Google Gemini API Key. If None, looks for GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not HAS_GEMINI:
            print("⚠️ Warning: 'google-generativeai' library not installed. Compliance Layer will run in PASSTHROUGH mode.")
            self.model = None
            return

        if not self.api_key:
            print("⚠️ Warning: No Gemini API Key found. Compliance Layer will run in PASSTHROUGH mode.")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("🛡️ Compliance Engine Armed & Ready.")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini: {e}")
                self.model = None

    def vet_response(self, draft_text, mood="Neutral"):
        """
        Review and improve the email draft.
        
        Args:
            draft_text (str): The generated email draft.
            mood (str): The detected mood of the customer (context).
            
        Returns:
            str: The approved (and possibly improved) text.
        """
        # Fail Open: If no model, return original text
        if not self.model:
            return draft_text

        try:
            # Construct Prompt
            prompt = f"""
            Act as a Senior Customer Support Compliance Officer.
            Review the following email draft intended for a customer.
            
            Context:
            - Customer Mood: {mood}
            
            Guidelines:
            1. Safety: Ensure no PII leaks (other than what's in the draft) and no toxic language.
            2. Tone: Ensure the tone is professional, empathetic, and helpful.
               - If Mood is 'Angry', ensure we are apologetic and reassuring.
               - If Mood is 'Happy', ensure we are warm and appreciative.
            3. Clarity: Ensure the message is clear and concise.
            
            Draft to Review:
            "{draft_text}"
            
            Output:
            Return ONLY the final improved version of the email. Do not add any conversational filler like "Here is the improved email". Just the email body.
            """
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                return response.text.strip()
            else:
                return draft_text
                
        except Exception as e:
            print(f"⚠️ Compliance Check Failed (Fail Open): {e}")
            return draft_text

if __name__ == "__main__":
    # Test Logic
    print("--- TESTING COMPLIANCE ENGINE ---")
    
    # Note: This requires GEMINI_API_KEY to be set in environment
    engine = ComplianceEngine()
    
    draft = "Hey you, we cant find your order. Check the number again."
    mood = "Angry"
    
    print(f"\nOriginal Draft:\n{draft}")
    print(f"\nMood: {mood}")
    
    vetted = engine.vet_response(draft, mood)
    print(f"\n🛡️ Vetted Response:\n{vetted}")
