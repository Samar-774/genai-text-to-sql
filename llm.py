from google import genai
from dotenv import load_dotenv
import os
from schema import SCHEMA
load_dotenv()

def get_explanation(prompt_text):
    client=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response=client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt_text
    )
    return response.text



def generate_sql(user_question):
    prompt = f"""
You are a SQL expert. Given the following database schema:

{SCHEMA}

Convert this question into a SQL SELECT query:
{user_question}

Return only the SQL query, nothing else. No markdown, no explanation.
"""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text