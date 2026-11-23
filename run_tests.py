"""
Direct test runner — no server needed.
Calls generate_sql() and executes against Postgres directly.
"""
import sys
import os
import time

os.chdir(r"c:\Users\KIIT0001\Desktop\genai-sql-project")
sys.path.insert(0, r"c:\Users\KIIT0001\Desktop\genai-sql-project")

from dotenv import load_dotenv
load_dotenv()

import psycopg2
from llm import generate_sql

QUESTIONS = [
    "How many customers are there?",
    "List all orders placed by customer with ID 5",
    "Which products have less than 10 items in inventory?",
    "What are the top 5 products by total revenue?",
    "Which customer spent the most money overall?",
]

DIFFICULTIES = [
    "Simple lookup",
    "Single join",
    "Two-table join",
    "Aggregation + join",
    "Multi-table aggregation",
]

results = []

for i, question in enumerate(QUESTIONS):
    print(f"\n{'='*60}", flush=True)
    print(f"Q{i+1} [{DIFFICULTIES[i]}]: {question}", flush=True)
    print(f"{'='*60}", flush=True)

    try:
        sql = generate_sql(question)
        sql_clean = sql.strip()
        # Strip markdown fences if present
        if sql_clean.startswith("```"):
            lines = sql_clean.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            sql_clean = "\n".join(lines).strip()

        print(f"Generated SQL:\n{sql_clean}", flush=True)

        conn = psycopg2.connect(
            host="localhost",
            database="erp_analytics",
            user="postgres",
            password=os.getenv("DB_PASSWORD")
        )
        cur = conn.cursor()
        cur.execute(sql_clean)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        cur.close()
        conn.close()

        print(f"Columns: {cols}", flush=True)
        print(f"Rows returned: {len(rows)}", flush=True)
        print(f"Preview: {rows[:3]}", flush=True)

        results.append({
            "id": i + 1,
            "difficulty": DIFFICULTIES[i],
            "question": question,
            "sql": sql_clean,
            "columns": cols,
            "row_count": len(rows),
            "preview": rows[:3],
            "status": "SUCCESS",
            "error": None,
        })
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        results.append({
            "id": i + 1,
            "difficulty": DIFFICULTIES[i],
            "question": question,
            "sql": sql_clean if 'sql_clean' in dir() else str(sql) if 'sql' in dir() else "N/A",
            "columns": None,
            "row_count": 0,
            "preview": None,
            "status": "ERROR",
            "error": str(e),
        })

# Write results
print("\n\nWriting results...", flush=True)
with open("test_results.md", "w", encoding="utf-8") as f:
    f.write("# NL-to-SQL Test Results — Baseline Run\n\n")
    f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}\n\n")

    success_count = 0
    for r in results:
        f.write(f"## Question {r['id']} — {r['difficulty']}\n")
        f.write(f"**Question:** {r['question']}\n\n")
        if r["status"] == "SUCCESS":
            f.write(f"**Generated SQL:**\n```sql\n{r['sql']}\n```\n\n")
            f.write(f"**Columns:** {r['columns']}\n\n")
            f.write(f"**Rows returned:** {r['row_count']}\n\n")
            f.write(f"**Preview (first 3 rows):** `{r['preview']}`\n\n")
            f.write("**Status:** ✅ Returned results\n\n")
            success_count += 1
        else:
            f.write(f"**Generated SQL:**\n```sql\n{r['sql']}\n```\n\n")
            f.write(f"**Status:** ❌ Error: `{r['error']}`\n\n")
        f.write("---\n\n")

    f.write(f"## Summary\n")
    f.write(f"- **Baseline accuracy:** {success_count}/{len(results)} returned results\n")

print(f"Done. {sum(1 for r in results if r['status'] == 'SUCCESS')}/{len(results)} succeeded.", flush=True)
