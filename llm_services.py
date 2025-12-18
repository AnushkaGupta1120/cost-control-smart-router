import os
import asyncio
from dotenv import load_dotenv
from groq import AsyncGroq
import google.generativeai as genai
from google.api_core import exceptions

# 1. Load environment variables
load_dotenv()

# 2. Setup Groq (For Simple/Medium tasks)
groq_api_key = os.environ.get("GROQ_API_KEY")
groq_client = AsyncGroq(api_key=groq_api_key) if groq_api_key else None

# 3. Setup Gemini (For Hard/Live tasks)
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

async def call_phi3(prompt: str):
    """Tier 1: Small/Fast (Llama-3.1-8b via Groq)"""
    if not groq_client: return {"model": "Error", "response": "GROQ_API_KEY missing"}
    try:
        completion = await groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            max_tokens=200,
        )
        return {
            "model": "Llama-3.1-8b (Groq)",
            "response": completion.choices[0].message.content,
            "cost": 0.00005
        }
    except Exception as e:
        return {"model": "Llama-3.1-8b", "response": f"Error: {str(e)}", "cost": 0}

async def call_llama70b(prompt: str):
    """Tier 2: Medium (Llama-3.3-70b via Groq)"""
    if not groq_client: return {"model": "Error", "response": "GROQ_API_KEY missing"}
    try:
        completion = await groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            max_tokens=500,
        )
        return {
            "model": "Llama-3.3-70b (Groq)",
            "response": completion.choices[0].message.content,
            "cost": 0.0005 
        }
    except Exception as e:
        return {"model": "Llama-3.3-70b", "response": f"Error: {str(e)}", "cost": 0}

async def call_gpt4o(prompt: str):
    """
    Tier 3: HARD -> Robust Google Gemini Strategy
    1. Try Gemini 2.0 Flash (Best, with Search)
    2. If Rate Limited (429), try Gemini 2.0 Flash Lite (Backup)
    3. If Search fails, retry WITHOUT search (Guaranteed Answer)
    """
    if not gemini_api_key:
        return {"model": "Error", "response": "GEMINI_API_KEY missing", "cost": 0}

    # Preference List: 2.0 Flash -> 2.0 Flash Lite -> 1.5 Flash
    models_to_try = [
        'gemini-2.0-flash',
        'gemini-2.0-flash-lite-preview-02-05',
        'gemini-1.5-flash'
    ]

    for model_id in models_to_try:
        try:
            # Configure Model
            model = genai.GenerativeModel(model_id)
            
            # ATTEMPT 1: Try with Google Search (Live Data)
            # Only 2.0 models consistently support 'google_search_retrieval' in the free tier
            if '2.0' in model_id:
                try:
                    response = await model.generate_content_async(
                        prompt,
                        tools='google_search_retrieval'
                    )
                    return {
                        "model": f"{model_id} (Live Search)", 
                        "response": response.text if response.text else "Search found no text.",
                        "cost": 0.001 
                    }
                except Exception as search_err:
                    # If Search fails (tool error), don't crash. Just continue to Attempt 2.
                    print(f"⚠️ Search failed on {model_id}: {search_err}")

            # ATTEMPT 2: Standard Generation (No Search)
            # This is the safety net. If search failed or model is 1.5, runs as standard LLM.
            response = await model.generate_content_async(prompt)
            return {
                "model": f"{model_id} (Standard)", 
                "response": response.text, 
                "cost": 0.001
            }

        except exceptions.ResourceExhausted:
            # This catches the 429 Rate Limit Error
            print(f"⚠️ Rate Limit hit on {model_id}. Switching to backup...")
            continue # Try the next model in the list
            
        except Exception as e:
            print(f"❌ Error on {model_id}: {e}")
            continue

    return {"model": "System Overloaded", "response": "All Google models are currently busy. Please wait 30 seconds.", "cost": 0}