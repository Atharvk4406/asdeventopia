import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Testing API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

try:
    genai.configure(api_key=api_key)
    # Test with gemini-1.5-flash
    model = genai.GenerativeModel('gemini-3-flash-preview')
    response = model.generate_content("Say hello!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
