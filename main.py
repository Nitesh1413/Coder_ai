from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import logging

# Apne local modules import kar rahe hain
from sandbox import execute_in_docker
from ai_agent import get_ai_code

# Professional logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - API_CORE - %(levelname)s - %(message)s')

# FastAPI app initialize karna
app = FastAPI(title="Zero-Cost Local AI Coder", version="1.0")

# Input/Output ka Data Structure (Pydantic Models)
class CodeRequest(BaseModel):
    requirement: str
    max_retries: int = 4  # AI maximum 4 baar try karega

class CodeResponse(BaseModel):
    success: bool
    attempts: int
    final_code: str
    output: str
    error_log: str = ""

@app.post("/generate", response_model=CodeResponse)
async def generate_and_execute(request: CodeRequest):
    logging.info(f"New Request: {request.requirement}")
    
    error_history = [] # AI ki temporary memory
    latest_code = ""
    latest_execution = {}

    # The Self-Healing Loop
    for attempt in range(1, request.max_retries + 1):
        logging.info(f"--- ATTEMPT {attempt}/{request.max_retries} ---")
        
        # Step 1: Get Code from Brain
        logging.info("Thinking... (Calling AI)")
        latest_code = await asyncio.to_thread(get_ai_code, request.requirement, error_history)
        
        # Step 2: Run in Sandbox
        logging.info("Executing code in Docker Sandbox...")
        latest_execution = await asyncio.to_thread(execute_in_docker, latest_code)
        
        # Step 3: Check Signal (If/Else)
        if latest_execution["success"]:
            logging.info(f"SUCCESS! Code worked on attempt {attempt}.")
            return CodeResponse(
                success=True,
                attempts=attempt,
                final_code=latest_code,
                output=latest_execution["stdout"]
            )
        else:
            logging.warning(f"FAILED on attempt {attempt}. Injecting error into memory.")
            # Error ko history me append karo taki AI loop me theek kar sake
            error_history.append({
                "code": latest_code,
                "error": latest_execution["stderr"]
            })
            
    # Agar 4 attempts ke baad bhi fail ho jaye
    logging.error("Max retries reached. AI failed to solve the problem.")
    return CodeResponse(
        success=False,
        attempts=request.max_retries,
        final_code=latest_code,
        output=latest_execution.get("stdout", ""),
        error_log=latest_execution.get("stderr", "Unknown Error")
    )