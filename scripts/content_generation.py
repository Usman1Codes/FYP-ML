import os
import json
import asyncio
import re
import random
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# ==========================================
# CONFIGURATION
# ==========================================

# Load API Key from .env manually
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")
GOOGLE_API_KEY = None

if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                try:
                    key, value = line.strip().split("=", 1)
                    if key == "GEMINI_API_KEY":
                        GOOGLE_API_KEY = value
                except ValueError:
                    pass

MODEL_NAME = "gemini-2.5-flash"
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "mood_training_data.json")
TARGET_PER_MOOD = 500
BATCH_SIZE = 20

# ==========================================
# MOOD LABELS & DEFINITIONS
# ==========================================
MOODS = [
    "Angry",
    "Happy",
    "Neutral",
    "Confused",
    "Urgent"
]

# ==========================================
# DIVERSITY MATRIX (Styles & Topics)
# ==========================================
# We mix these to ensure "Angry" isn't just about "Late Orders".
TOPICS = [
    "Order Status (Late/Missing)",
    "Product Defect/Broken",
    "Return/Refund Request",
    "Account Access/Password",
    "Product Question (Specs/Stock)",
    "Shipping Address Change",
    "Billing/Payment Issue",
    "General Feedback"
]

STYLES = {
    "The Rusher": "Short, typos, lowercase, no punctuation. 'where is my order'",
    "The Formal": "Excessively polite, proper grammar, 'Dear Sir/Madam'.",
    "The Rant": "Long, emotional, storytelling. Mentions personal life.",
    "The Direct": "To the point. 'I need a refund.' No fluff.",
    "The Confused": "Doesn't understand the process. 'How do I click this?'",
    "The Broken English": "Grammar errors typical of non-native speakers, but understandable.",
    "The Karen/Kevin": "Demanding, mentions 'manager', 'lawyer', or 'never buying again'.",
    "The Happy Camper": "Overly enthusiastic, uses emojis, 'Love your stuff!'."
}

# ==========================================
# PROMPT ENGINEERING
# ==========================================
def build_prompt(mood, topic, style_name, style_desc, count):
    return f"""
    Generate exactly {count} unique customer support emails.
    
    TARGET MOOD: "{mood}"
    TOPIC: "{topic}"
    WRITING STYLE: "{style_name}" ({style_desc})
    
    CRITICAL INSTRUCTIONS:
    1. **DIVERSITY:** Each email must be unique. Do not repeat phrases.
    2. **REALISM:** 
       - If style is "The Rusher", use "u" for "you", skip apostrophes.
       - If mood is "Neutral", just ask the question plainly.
       - If mood is "Confused", ask vague questions like "what is haping".
    3. **CONTEXT:** Use realistic fake Order IDs (#12345), Product Names, and Dates.
    4. **NO HEADERS:** Return ONLY the raw email body text. No "Subject:", No "Email 1:".
    
    OUTPUT FORMAT:
    Return ONLY a valid JSON object:
    {{ "emails": ["email text 1", "email text 2"] }}
    """

# ==========================================
# FILE HANDLING
# ==========================================
def load_data():
    if not os.path.exists(OUTPUT_FILE):
        return []
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ==========================================
# GENERATION LOGIC
# ==========================================
async def generate_batch(model, mood, topic, style_name, style_desc):
    prompt = build_prompt(mood, topic, style_name, style_desc, BATCH_SIZE)
    
    for attempt in range(3):
        try:
            response = await model.generate_content_async(prompt)
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            if not clean_text: continue
            
            data = json.loads(clean_text)
            emails = data.get("emails", [])
            
            # Format as labeled data
            return [{"text": e, "mood": mood} for e in emails]
            
        except Exception as e:
            print(f"   ⚠️ Retry {attempt+1} for {mood}/{style_name}: {e}")
            await asyncio.sleep(2)
            
    return []

async def process_mood(mood, semaphore):
    async with semaphore:
        print(f"[{mood}] Starting generation...")
        
        # Configure Model
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={"response_mime_type": "application/json", "temperature": 0.9}
        )
        
        # Check Progress
        all_data = load_data()
        current_mood_data = [d for d in all_data if d["mood"] == mood]
        count = len(current_mood_data)
        
        if count >= TARGET_PER_MOOD:
            print(f"[{mood}] ✅ Already has {count} emails. Skipping.")
            return

        while count < TARGET_PER_MOOD:
            # Randomly select Topic and Style for this batch to ensure variety
            topic = random.choice(TOPICS)
            style_name, style_desc = random.choice(list(STYLES.items()))
            
            batch = await generate_batch(model, mood, topic, style_name, style_desc)
            
            if batch:
                # Load, Append, Save (Inefficient but safe for resume)
                current_all_data = load_data()
                current_all_data.extend(batch)
                save_data(current_all_data)
                
                count += len(batch)
                print(f"   -> [{mood}] +{len(batch)} ({style_name} / {topic}) | Total: {count}")
            
            await asyncio.sleep(1) # Rate limit safety

        print(f"[{mood}] 🎉 Completed {count} emails.")

async def main():
    if not GOOGLE_API_KEY:
        print("❌ ERROR: GEMINI_API_KEY not found in .env")
        return

    print(f"🚀 Starting Data Generation for {len(MOODS)} Moods...")
    print(f"🎯 Target: {TARGET_PER_MOOD} emails per mood.")
    print(f"📂 Output: {OUTPUT_FILE}")

    # Semaphore: 2 concurrent tasks to speed up but respect limits
    semaphore = asyncio.Semaphore(2)
    tasks = [process_mood(m, semaphore) for m in MOODS]
    await asyncio.gather(*tasks)
    print("\n✅ All Data Generation Complete!")

if __name__ == "__main__":
    asyncio.run(main())