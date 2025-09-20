import json
import requests
from functools import wraps


def ai_enhance(prompt_template: str):
    """Add AI analysis to any function output"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Run original function
            result = func(*args, **kwargs)
            
            # Get AI analysis
            prompt = prompt_template.format(result=result)
            ai_response = call_ai(prompt)
            
            return {"original": result, "ai_analysis": ai_response}
        return wrapper
    return decorator


def call_ai(prompt: str) -> str:
    """Simple AI API call"""
    response = requests.post(
        "http://127.0.0.1:4000/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-1234"
        },
        json={
            "model": "gpt-oss-20b (OpenRouter)",
            "max_tokens": 10000,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return response.json()["choices"][0]["message"]["content"]


# Usage Examples

@ai_enhance("Analyze this vulnerability scan for critical risks:\n{result}")
def vulnerability_scan(target: str) -> str:
    return f"Found 3 critical SQLi, 5 XSS on {target}"


@ai_enhance("Extract key security findings as JSON:\n{result}")
def log_analysis(logfile: str) -> str:
    return "Failed login from 192.168.1.100, admin account locked"


# Usage
result = vulnerability_scan("app.example.com")
print(result["original"])     # Original scan output  
print("-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-")
print(result["ai_analysis"])  # AI risk assessment
