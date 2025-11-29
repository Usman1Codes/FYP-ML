# import os
# import json
# import asyncio
# import time
# import google.generativeai as genai
# from google.generativeai.types import HarmCategory, HarmBlockThreshold

# # ==========================================
# # CONFIGURATION
# # ==========================================

# # SECURITY WARNING: You have hardcoded your API key here. 
# # Do not share this script publicly (GitHub, forums) without removing this line.
# GOOGLE_API_KEY = "AIzaSyCnI5mY1ggt4epJwiYwY-72s61AWg2CQMw"

# # Model: Using gemini-2.5-flash for the 65k output limit
# MODEL_NAME = "gemini-2.5-flash" 

# OUTPUT_DIR = "generated_emails_unlimited"
# TARGET_TOTAL_EMAILS = 500
# BATCH_SIZE = 50 

# # ==========================================
# # FIX: RE-ADDED THE MISSING LABELS LIST
# # ==========================================
# LABELS = [
#     "order_status_inquiry",
#     "product_information_question",
#     "account_password_reset",
#     "general_faq_question",
#     "inventory_stock_availability"
# ]

# # ==========================================
# # 1. PERSONA DEFINITIONS
# # ==========================================
# STYLES = {
#     "The Rusher": "Mobile user. Lowercase, typos (u, r), no punctuation. Blunt.",
#     "The Irrate Customer": "Angry. Caps lock on keywords. Demands refund/manager. 'Never buying again'. Long rants.",
#     "The Formal": "Excessively professional. 'Kind Regards', 'Inquiry regarding'. Perfect grammar.",
#     "The Senior": "Polite but confused. Mentions grandkids/weather. 'Not sure how to click'.",
#     "The Minimalist": "Subject line only. 3-5 words max. e.g. 'return help'.",
#     "The Storyteller": "Rambling. Includes personal life details irrelevant to the product.",
#     "The Broken English": "Grammar errors typical of translation. Polite but awkward phrasing.",
#     "The Techie": "Asks about specs, SKUs, firmware, material composition. Cold tone.",
#     "The Anxious": "Worried about shipping dates. 'Need this by Friday!', 'Is it safe?'.",
#     "The Vague": "No context. 'It is broken'. 'Where is it'. No order number given."
# }

# # ==========================================
# # 2. PROMPT BUILDER
# # ==========================================
# def build_prompt(label, style_name, style_desc, count):
#     return f"""
#     Generate exactly {count} customer support emails for: "{label}".
    
#     PERSONA: {style_name}
#     DESCRIPTION: {style_desc}
    
#     RULES:
#     1. STRICTLY follow the Persona.
#     2. Generate realistic fake Order IDs, Dates, and Product Names.
#     3. Output PURE JSON only. 
    
#     JSON SCHEMA:
#     {{ "emails": ["email 1", "email 2"] }}
#     """

# # ==========================================
# # 3. GENERATION LOGIC
# # ==========================================

# async def generate_batch(model, label, style_name, style_desc):
#     prompt = build_prompt(label, style_name, style_desc, BATCH_SIZE)
    
#     for attempt in range(3):
#         try:
#             response = await model.generate_content_async(prompt)
            
#             clean_text = response.text.replace("```json", "").replace("```", "").strip()
            
#             # Simple Validation
#             if not clean_text:
#                 raise ValueError("Empty response received")
                
#             data = json.loads(clean_text)
#             return data.get("emails", [])

#         except Exception as e:
#             print(f"   [Retrying] Error on {style_name}: {e}")
#             await asyncio.sleep(5) 
            
#     return []

# async def process_label(label, semaphore):
#     async with semaphore:
#         print(f"[{label}] Starting...")
#         genai.configure(api_key=GOOGLE_API_KEY)
        
#         # Using 65k token limit to prevent cut-off issues
#         model = genai.GenerativeModel(
#             model_name=MODEL_NAME,
#             generation_config={
#                 "response_mime_type": "application/json", 
#                 "temperature": 1.0,
#                 "max_output_tokens": 65536 
#             },
#             safety_settings={
#                 HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
#                 HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
#                 HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
#                 HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
#             }
#         )
        
#         emails = []
#         needed_batches = (TARGET_TOTAL_EMAILS // BATCH_SIZE) // len(STYLES) + 1
        
#         for _ in range(needed_batches):
#             for style, desc in STYLES.items():
#                 if len(emails) >= TARGET_TOTAL_EMAILS:
#                     break
                    
#                 batch = await generate_batch(model, label, style, desc)
#                 emails.extend(batch)
#                 print(f"   -> {style}: +{len(batch)} emails")
                
#                 # Small sleep to be safe with rate limits
#                 await asyncio.sleep(2)
            
#             if len(emails) >= TARGET_TOTAL_EMAILS:
#                 break
            
#         # Save
#         if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
#         final_data = {"label": label, "count": len(emails), "emails": emails[:TARGET_TOTAL_EMAILS]}
        
#         with open(f"{OUTPUT_DIR}/{label}.json", 'w', encoding='utf-8') as f:
#             json.dump(final_data, f, indent=2, ensure_ascii=False)
        
#         print(f"[{label}] Done. Saved {len(final_data['emails'])} emails.")

# async def main():
#     if GOOGLE_API_KEY == "YOUR_GEMINI_API_KEY":
#         print("ERROR: Set API Key.")
#         return

#     # Semaphore controls parallel execution to avoid Rate Limit Errors
#     semaphore = asyncio.Semaphore(1) 
    
#     tasks = [process_label(l, semaphore) for l in LABELS]
#     await asyncio.gather(*tasks)

# if __name__ == "__main__":
#     asyncio.run(main())


import os
import json
import asyncio
import re
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# ==========================================
# CONFIGURATION
# ==========================================

# API Key provided by you
GOOGLE_API_KEY = "AIzaSyCnI5mY1ggt4epJwiYwY-72s61AWg2CQMw"

MODEL_NAME = "gemini-2.5-flash"
OUTPUT_DIR = "generated_emails_realism"
TARGET_TOTAL_EMAILS = 500
BATCH_SIZE = 20  # Smaller batch size = higher quality/focus

# ==========================================
# INTENT LABELS
# ==========================================
LABELS = [
    "order_status_inquiry",
    "product_information_question",
    "account_password_reset",
    "general_faq_question",
    "inventory_stock_availability"
]

# ==========================================
# REALISTIC STYLES (GROUNDED)
# ==========================================
# Replaced caricatures with realistic email types
STYLES = {
    "Direct & Brief": "Short, to the point. No fluff. Often skips greetings. Typical of busy people.",
    "Polite & Formal": "Uses proper greetings (Hi, Hello), complete sentences, and polite closings (Thanks, Best regards).",
    "Frustrated but Civil": "Customer is annoyed by a delay or issue but maintains composure. Not screaming, just stern.",
    "Mobile/Casual": "Lowercase start sentences occasionally, 'sent from iphone' style, minor grammar relaxations, but FULLY readable.",
    "Context Heavy": "Explains *why* they need the answer (e.g., 'need this for a birthday Friday', 'moving houses soon').",
    "Confusion/Help Needed": "Customer doesn't understand the interface or process. Asks clarifying questions."
}

# ==========================================
# PROMPT ENGINEERING
# ==========================================
def build_prompt(label, style_name, style_desc, count):
    # Specific instructions to avoid AI-isms and headers
    return f"""
    Generate exactly {count} raw customer support email bodies for the intent: "{label}".
    
    STYLE: {style_name}
    STYLE GUIDE: {style_desc}
    
    CRITICAL INSTRUCTIONS:
    1. **NO HEADERS:** Do NOT include "Subject:", "Body:", "Email 1:", or numbering. Just the raw text.
    2. **REALISM:** Do not use gibberish. Use natural English. If using the "Mobile" style, use standard abbreviations (e.g., 'havent' instead of 'haven't') but do not use "wurz my ordu".
    3. **CONTENT:** specific to {label}. Use realistic fake order IDs (mix of numbers/letters like #10293, #ORD-992).
    4. **VARIETY:** Mix lengths. Some should be one sentence. Some should be 3-4 sentences.
    
    OUTPUT FORMAT:
    Return ONLY a valid JSON object with this structure:
    {{ "emails": ["raw email text 1", "raw email text 2"] }}
    """

# ==========================================
# FILE HANDLING (INCREMENTAL SAVING)
# ==========================================

def load_existing_data(filepath):
    if not os.path.exists(filepath):
        return {"label": "", "count": 0, "emails": []}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"label": "", "count": 0, "emails": []}

def save_incremental(label, new_emails):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    filepath = f"{OUTPUT_DIR}/{label}.json"
    data = load_existing_data(filepath)
    
    # Update data
    data["label"] = label
    if "emails" not in data: data["emails"] = []
    
    # Clean and add new emails
    cleaned_batch = []
    for email in new_emails:
        # Regex to strip "Subject: ..." if the AI accidentally adds it
        cleaned = re.sub(r'^Subject:.*?\n', '', email, flags=re.IGNORECASE)
        cleaned = re.sub(r'^Body:\s*', '', cleaned, flags=re.IGNORECASE).strip()
        cleaned_batch.append(cleaned)

    data["emails"].extend(cleaned_batch)
    data["count"] = len(data["emails"])
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return data["count"]

# ==========================================
# GENERATION LOGIC
# ==========================================

async def generate_batch(model, label, style_name, style_desc):
    prompt = build_prompt(label, style_name, style_desc, BATCH_SIZE)
    
    for attempt in range(3):
        try:
            response = await model.generate_content_async(prompt)
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            
            if not clean_text: continue

            try:
                data = json.loads(clean_text)
                return data.get("emails", [])
            except json.JSONDecodeError:
                # Fallback: Try to verify if it's a list even if JSON is slightly broken
                pass
        except Exception as e:
            print(f"   [Retrying] {style_name}: {e}")
            await asyncio.sleep(2)
            
    return []

async def process_label(label, semaphore):
    async with semaphore:
        print(f"[{label}] Starting generation...")
        genai.configure(api_key=GOOGLE_API_KEY)
        
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={
                "response_mime_type": "application/json", 
                "temperature": 0.85, # Slightly lowered for more coherent realism
                "max_output_tokens": 8192 
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # Check current progress
        filepath = f"{OUTPUT_DIR}/{label}.json"
        current_data = load_existing_data(filepath)
        current_count = len(current_data.get("emails", []))
        
        if current_count >= TARGET_TOTAL_EMAILS:
            print(f"[{label}] Already has {current_count} emails. Skipping.")
            return

        # Loop until target reached
        while current_count < TARGET_TOTAL_EMAILS:
            for style, desc in STYLES.items():
                if current_count >= TARGET_TOTAL_EMAILS: break
                
                batch = await generate_batch(model, label, style, desc)
                
                if batch:
                    # Save immediately (Incremental Saving)
                    current_count = save_incremental(label, batch)
                    print(f"   -> {style}: Saved +{len(batch)} (Total: {current_count})")
                
                # Rate limit protection
                await asyncio.sleep(2)

        print(f"[{label}] Completed with {current_count} emails.")

async def main():
    if GOOGLE_API_KEY == "YOUR_GEMINI_API_KEY":
        print("ERROR: Please set your API Key.")
        return

    # Semaphore to prevent hitting rate limits (1 active label at a time is safest for Free Tier)
    semaphore = asyncio.Semaphore(1) 
    
    tasks = [process_label(l, semaphore) for l in LABELS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())