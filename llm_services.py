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

# 3. Setup Gemini (For Live/Complex tasks)
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

async def call_phi3(prompt: str):
    """Tier 1: Small/Fast (Llama-3.1-8b via Groq)"""
    if not groq_client: return {"model": "Error", "response": "GROQ_API_KEY missing"}
    try:
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a concise assistant."},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.1-8b-instant",
            temperature=0.5,
            max_tokens=200,
        )
        return {
            "model": "Llama-3.1-8b (Groq)",
            "response": chat_completion.choices[0].message.content,
            "cost": 0.00005
        }
    except Exception as e:
        return {"model": "Llama-3.1-8b", "response": f"Error: {str(e)}", "cost": 0}

async def call_llama70b(prompt: str):
    """Tier 2: Medium (Llama-3.3-70b via Groq)"""
    if not groq_client: return {"model": "Error", "response": "GROQ_API_KEY missing"}
    try:
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert analyst."},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=500,
        )
        return {
            "model": "Llama-3.3-70b (Groq)",
            "response": chat_completion.choices[0].message.content,
            "cost": 0.0005 
        }
    except Exception as e:
        return {"model": "Llama-3.3-70b", "response": f"Error: {str(e)}", "cost": 0}

async def call_gpt4o(prompt: str):
    """
    Tier 3: HARD -> Smart Fallback with DYNAMIC TOOLING
    """
    if not gemini_api_key:
        return {"model": "Error", "response": "GEMINI_API_KEY missing", "cost": 0}

    # Order of preference: 
    # 1. Gemini 2.0 (Best, uses 'google_search_retrieval')
    # 2. Gemini 1.5 (Stable Backup, uses 'google_search')
    models_to_try = [
        'gemini-2.0-flash', 
        'gemini-flash-latest' 
    ]

    for model_id in models_to_try:
        try:
            # DYNAMIC TOOL SELECTION
            if '2.0' in model_id:
                search_tool = 'google_search_retrieval'
            else:
                search_tool = 'google_search'

            model = genai.GenerativeModel(model_id)
            
            # Try with Search
            response = await model.generate_content_async(
                prompt,
                tools=search_tool 
            )
            
            return {
                "model": f"{model_id} (Live)", 
                "response": response.text if response.text else "Search found no text.",
                "cost": 0.001 
            }

        except exceptions.ResourceExhausted:
            print(f"⚠️ Rate Limit on {model_id}. Switching...")
            continue # Try next model
            
        except Exception as e:
            # FINAL FALLBACK: If search tool fails, run WITHOUT search
            print(f"❌ Error on {model_id} ({e}). Retrying without search...")
            try:
                model = genai.GenerativeModel(model_id)
                response = await model.generate_content_async(prompt) # No tools
                return {
                    "model": f"{model_id} (Offline Mode)", 
                    "response": response.text, 
                    "cost": 0.001
                }
            except:
                continue

    return {"model": "System Overloaded", "response": "Please wait 60 seconds (Google Quota Exceeded).", "cost": 0}