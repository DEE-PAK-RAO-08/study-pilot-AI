import os
import urllib.request
import urllib.error
import json

# Try to load dotenv, but it's optional (env vars can be set directly on Render)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, assume env vars are set directly

def get_openai_answer(query: str, context_text: str = "", history: list = None) -> dict:
    """
    Get an answer from OpenAI (ChatGPT) using standard library (urllib).
    Returns None if offline or no key.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
        
    url = "https://api.openai.com/v1/chat/completions"
    
    # Construct messages array
    messages = [
        {
            "role": "system", 
            "content": """You are Study Pilot AI, an advanced educational assistant for university students.
            Answer the student's question accurately, concisely, and academically.
            Use clear formatting (bullet points, bold text).
            Maintain a friendly, encouraging, and helpful tone."""
        }
    ]
    
    # Add history if available
    if history:
        for msg in history:
            role = "user" if msg.get('type') == 'user' else "assistant"
            messages.append({"role": role, "content": msg.get('content', '')})
            
    # Add current query
    user_message = f"Question: {query}"
    if context_text:
        user_message += f"\n\nContext from course materials:\n{context_text}"
    
    messages.append({"role": "user", "content": user_message})
        
    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1000
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            answer_text = result['choices'][0]['message']['content']
            
            return {
                'answer': answer_text,
                'citations': [],
                'confidence': 0.99,
                'sources': ['ChatGPT (Cloud Logic)']
            }
            
    except Exception as e:
        print(f"Cloud LLM request failed: {e}")
        return None
