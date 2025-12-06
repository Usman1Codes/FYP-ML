import os
import sys
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.m09_flow_manager import FlowManager

def type_writer(text, delay=0.01):
    """Simulate typing effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    print("\n" + "="*60)
    print("🤖 JUNO AUTOMATION ENGINE - INTERACTIVE DEMO")
    print("="*60)
    
    # Initialize System
    print("⏳ Initializing System... (This may take a moment)")
    try:
        manager = FlowManager()
        print("✅ System Ready!\n")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return

    # Use Default Identity for Demo
    user_email = "demo_user@example.com"
    
    print(f"\n👋 Connected as: {user_email}")
    print("   Type 'exit' or 'quit' to end the session.\n")
    print("-" * 60)

    while True:
        try:
            # Get User Input
            user_input = input(f"\n👤 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue

            # Process Input
            print("\n🤖 JUNO is thinking...", end="\r")
            
            # Capture start time for latency check
            start_time = time.time()
            
            response = manager.process_email(user_email, user_input)
            
            elapsed = time.time() - start_time
            
            # Clear "thinking" line
            print(" " * 30, end="\r")
            
            # Display Response
            print(f"🤖 JUNO ({elapsed:.2f}s):")
            print("-" * 20)
            type_writer(response.strip())
            print("-" * 20)
            
            # Optional: Display Debug Info (Ticket State)
            ticket = manager.ticket_manager.get_ticket(user_email)
            if ticket:
                print(f"   [DEBUG] Ticket: {ticket.ticket_id} | Status: {ticket.status} | Mood: {ticket.mood}")

        except KeyboardInterrupt:
            print("\n\n👋 Session Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
