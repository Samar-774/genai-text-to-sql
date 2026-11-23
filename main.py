from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import psycopg2
import os

from llm import get_explanation, generate_sql
from guardrails import execute_safe
from insights import (
    get_low_stock_insight,
    get_revenue_concentration_insight,
    get_customer_spending_insight,
)

load_dotenv()
app = FastAPI(title="ERP Analytics GenAI SQL API")


import urllib.parse

def get_db_params():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        result = urllib.parse.urlparse(database_url)
        return {
            "host": result.hostname,
            "database": result.path[1:],
            "user": result.username,
            "password": result.password,
            "port": result.port,
        }
    return {
        "host": "localhost",
        "database": "erp_analytics",
        "user": "postgres",
        "password": os.getenv("DB_PASSWORD"),
    }


@app.get("/ping")
def ping():
    return {"status": "ok"}


@app.get("/query")
def query(q: str):
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty.")

    # 1. Generate SQL from natural language
    try:
        sql = generate_sql(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {e}")

    # 2. Run through guardrails and execute
    result = execute_safe(sql, get_db_params(), timeout_seconds=10)

    if not result["success"]:
        return {
            "sql": result["sql"],
            "columns": [],
            "rows": [],
            "error": result["error"],
        }

    return {
        "sql": result["sql"],
        "columns": result["columns"],
        "rows": result["rows"],
        "error": None,
    }


@app.get("/insights")
def insights():
    """Returns grounded business insights with Python-computed statistics and LLM summaries."""
    db_params = get_db_params()
    try:
        low_stock = get_low_stock_insight(db_params)
        revenue_concentration = get_revenue_concentration_insight(db_params)
        customer_spending = get_customer_spending_insight(db_params)
        return {
            "insights": [
                low_stock,
                revenue_concentration,
                customer_spending,
            ]
        }
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {traceback.format_exc()}")
