import google.generativeai as genai
import os
import time


TEST_MODE = True 

API_KEY = os.environ.get("GEMINI_API_KEY", "dummy_key")
if not TEST_MODE:
    genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = """You are an elite Python backend developer. 
Your ONLY job is to write pure, executable Python code based on the user's requirement.
RULES:
1. Do NOT wrap code in markdown blocks.
2. Only output raw text that can be directly executed by a Python interpreter."""

if not TEST_MODE:
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)

def get_ai_code(prompt: str, error_history: list = None) -> str:
    """AI se code generate karwata hai. Test mode me fake code deta hai."""
    

    if TEST_MODE:
        print("\n[MOCK AI] Thinking... (Simulating 2 seconds delay)")
        time.sleep(2) 
        
        
        if not error_history:
            print("[MOCK AI] Attempt 1: Giving BAD code intentionally to test Docker and Loop.")
            return "print('Hello user, main division kar raha hu...')\nresult = 10 / 0\nprint(result)"
            
        
        else:
            print("[MOCK AI] Attempt 2: Giving GOOD code to test Success exit.")
            return "print('Pichli baar error aayi thi, ab maine theek kar diya hai!')\nresult = 10 / 2\nprint(f'Answer is {result}')"

    
    full_prompt = f"User Requirement: {prompt}\n\n"
    if error_history:
        full_prompt += "--- PREVIOUS ATTEMPTS & ERRORS ---\n"
        for i, err in enumerate(error_history):
            full_prompt += f"Attempt {i+1} Failed Code:\n{err['code']}\n"
            full_prompt += f"Error Received:\n{err['error']}\n\n"
        full_prompt += "Please fix the above errors and provide the corrected code."

    response = model.generate_content(full_prompt)
    raw_code = response.text.strip()
    
    if raw_code.startswith("```python"):
        raw_code = raw_code[9:]
    if raw_code.endswith("```"):
        raw_code = raw_code[:-3]

    return raw_code.strip()
