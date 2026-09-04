from google import genai
from dotenv import load_dotenv
import os
load_dotenv()

def get_explanation(prompt_text):
    client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response=client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt_text
    )
    return response.text