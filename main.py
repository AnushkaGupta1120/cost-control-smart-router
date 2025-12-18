from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware # <--- NEW
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text # <--- NEW
from router_engine import classify_difficulty
from llm_services import call_phi3, call_llama70b, call_gpt4o
from database import get_db, RequestLog

app = FastAPI(title="Cost-Control Smart Router")

# 1. Enable CORS (Allows React to talk to this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRequest(BaseModel):
    prompt: str

# 2. The Generation Endpoint (Existing)
@app.post("/generate")
async def smart_generate(request: UserRequest, db: Session = Depends(get_db)):
    user_prompt = request.prompt
    difficulty = classify_difficulty(user_prompt)
    
    # Routing Logic
    result = {}
    if difficulty == "SIMPLE":
        result = await call_phi3(user_prompt)
    elif difficulty == "MEDIUM":
        result = await call_llama70b(user_prompt)
    else:
        result = await call_gpt4o(user_prompt)

    # Cost Calculation
    PRICE_GPT4 = 5.00
    PRICE_LLAMA_SMALL = 0.05 
    PRICE_LLAMA_LARGE = 0.50
    
    est_tokens = max(1, len(user_prompt) / 4) 
    hypothetical_gpt4_cost = (est_tokens / 1_000_000) * PRICE_GPT4
    
    if difficulty == "SIMPLE":
        actual_cost = (est_tokens / 1_000_000) * PRICE_LLAMA_SMALL
    elif difficulty == "MEDIUM":
        actual_cost = (est_tokens / 1_000_000) * PRICE_LLAMA_LARGE
    else:
        actual_cost = hypothetical_gpt4_cost
        
    savings = hypothetical_gpt4_cost - actual_cost

    # Log to DB
    try:
        new_log = RequestLog(
            prompt_text=user_prompt,
            difficulty_level=difficulty,
            model_used=result.get("model", "Unknown"),
            token_count=int(est_tokens),
            actual_cost=actual_cost,
            hypothetical_cost_gpt4=hypothetical_gpt4_cost,
            money_saved=savings
        )
        db.add(new_log)
        db.commit()
    except Exception as e:
        print(f"Database Logging Failed: {e}")

    return {
        "router_decision": difficulty,
        "model_used": result.get("model", "Unknown"),
        "content": result.get("response", "Error generating response"),
        "cost_saved": f"${savings:.8f}" 
    }

# 3. NEW: Logs Endpoint for React Dashboard
@app.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    # Fetch last 50 requests
    logs = db.query(RequestLog).order_by(RequestLog.timestamp.desc()).limit(50).all()
    return logs

from mangum import Mangum
handler = Mangum(app)