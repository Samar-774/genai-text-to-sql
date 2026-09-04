from fastapi import FastAPI
from dotenv import load_dotenv
import psycopg2
import os
from llm import get_explanation
app=FastAPI()
load_dotenv()

@app.get("/ping")
def ping():
    conn = psycopg2.connect(
        host="localhost",
        database="erp_analytics",
        user="postgres",
        password=os.getenv("DB_PASSWORD")
    )
    cur=conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM customers"
    )
    result=cur.fetchone()
    cur.close()
    conn.close()

    prompt=f"my dataset has {result[0]} rows what does that mean it is a customer dataset explain the number of rows in one short para"
    explanation=get_explanation(prompt)
    return {"total_customers":result[0],"explanation":explanation}
