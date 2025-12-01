"""
Interactive Tester for JUNO Automation Engine.
Uses Google Gemini to generate realistic test scenarios and allows
the user to interact with the engine in a loop.
"""

import os
import sys
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

from src.m09_flow_manager import FlowManager

# Scenarios Definition
SCENARIOS = {
    "1": {"name": "Order Status - Angry", "prompt": "Write a short, angry email from a customer named John who hasn't received his order #12345 yet. He ordered it 2 weeks ago."},
    "2": {"name": "Order Status - Neutral (Missing ID)", "prompt": "Write a short email from a customer named Sarah asking where her order is. Do not include the order ID."},
    "3": {"name": "Return Policy - Confused", "prompt": "Write a short email from a customer named Mike who is confused about the return policy for sale items."},
    "4": {"name": "Product Inquiry - Happy", "prompt": "Write a short, happy email from a customer named Lisa asking if you have the 'Vintage Leather Jacket' in stock."},
    "5": {"name": "Custom Input", "prompt": None}
}

def generate_email(prompt, api_key):
    """Generate an email using Gemini."""
    if not HAS_GEMINI or not api_key:
        return "Error: Gemini API not available. Please enter text manually."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating email: {e}"

def main():
    print("==========================================")
    print("   JUNO ENGINE - INTERACTIVE TESTER       ")
    print("==========================================")
    
    # Initialize Engine
    # Initialize Engine
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Load .env manually
    env_path = os.path.join(project_root, ".env")
    print(f"🔍 Looking for .env at: {env_path}")
    if os.path.exists(env_path):
        print("   ✅ Found .env file.")
        with open(env_path, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    try:
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value
                        if key == "GEMINI_API_KEY":
                            print("   ✅ Loaded GEMINI_API_KEY")
                    except ValueError:
                        pass # Skip malformed lines
    else:
        print("   ❌ .env file NOT found.")

    manager = FlowManager(project_root)
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("⚠️  Warning: GEMINI_API_KEY not found in environment.")
        print("   Auto-generation of scenarios will be disabled.")
    
    while True:
        print("\nSelect a Scenario:")
        for key, val in SCENARIOS.items():
            print(f"{key}. {val['name']}")
        print("q. Quit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice.lower() == 'q':
            break
            
        if choice not in SCENARIOS:
            print("Invalid choice.")
            continue
            
        scenario = SCENARIOS[choice]
        user_id = f"test_user_{int(time.time())}@example.com"
        
        # 1. Generate Initial Email
        if choice == "5":
            email_text = input("\nEnter your email text: ")
        else:
            print(f"\n🤖 Generating scenario: {scenario['name']}...")
            if api_key and HAS_GEMINI:
                email_text = generate_email(scenario['prompt'], api_key)
                print(f"\n📨 Generated Email:\n---\n{email_text}\n---")
            else:
                print("❌ Cannot generate (No API Key). Please type manually:")
                email_text = input("Email text: ")

        # 2. Conversation Loop
        while True:
            # Process through JUNO
            print("\n⚙️  Processing...")
            response = manager.process_email(user_id, email_text)
            
            print(f"\n🤖 JUNO Reply:\n{response}")
            
            # Check if ticket is resolved (simple check based on response text or internal state)
            # For this script, we just ask the user if they want to reply.
            
            print("\n------------------------------------------")
            action = input("Reply? (Type reply or press Enter to finish scenario): ").strip()
            
            if not action:
                break
                
            email_text = action

    print("\nExiting Tester. Goodbye!")

if __name__ == "__main__":
    main()
