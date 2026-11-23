from google import genai
from dotenv import load_dotenv
import os
import re
from schema import SCHEMA
load_dotenv()


def sanitize_sql(raw: str) -> str:
    """Strip markdown fences, whitespace, and trailing semicolons from LLM output."""
    # Remove ```sql ... ``` markdown fences
    cleaned = re.sub(r"```(?:sql)?\s*\n?(.*?)\n?\s*```", r"\1", raw, flags=re.DOTALL)
    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()
    # Strip trailing semicolons
    cleaned = cleaned.rstrip(";").rstrip()
    return cleaned


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

Here are some example questions and their correct SQL:


Question: Which products have less than 10 items in inventory
SQL: SELECT products.product_name FROM products 
JOIN inventory ON products.product_id = inventory.prod_id 
WHERE inventory.quantity_left < 10;

Question: List the top 3 customers by total amount spent?
SQL: SELECT customers.name, SUM(order_items.quantity_bought * order_items.price) AS total_spent FROM customers 
JOIN orders ON customers.customer_id = orders.customer_id 
JOIN order_items ON orders.order_id = order_items.order_id 
GROUP BY customers.customer_id, customers.name ORDER BY total_spent DESC LIMIT 3;

Convert this question into a SQL SELECT query:
{user_question}

Return only the SQL query, nothing else. No markdown, no explanation.
"""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return sanitize_sql(response.text)
