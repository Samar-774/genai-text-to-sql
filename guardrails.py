import re
import psycopg2


DISALLOWED_KEYWORDS = [
    "DELETE",
    "DROP",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "EXECUTE",
]


def validate_sql(sql: str) -> tuple[bool, str]:
    """Validate whether an LLM-generated SQL query is safe to execute.

    Rules:
    1. Must begin with SELECT or WITH (case-insensitive).
    2. Must not contain destructive DDL/DML keywords as standalone tokens.
    3. Must not execute multiple statements separated by semicolons.
    """
    cleaned = sql.strip().rstrip(";")

    if not cleaned:
        return False, "Query is empty."

    # Check multiple statements (semicolon followed by non-whitespace)
    if ";" in cleaned:
        return False, "Multiple statements are not permitted."

    # Check starting statement type
    first_token_match = re.match(r"^\s*([A-Za-z]+)", cleaned)
    if not first_token_match:
        return False, "Could not determine SQL statement type."

    first_word = first_token_match.group(1).upper()
    if first_word not in ("SELECT", "WITH"):
        return False, f"Only SELECT/WITH read queries are allowed. Found: {first_word}"

    # Check for disallowed standalone keywords (avoid substring false positives)
    for kw in DISALLOWED_KEYWORDS:
        if re.search(rf"\b{kw}\b", cleaned, flags=re.IGNORECASE):
            return False, f"Disallowed SQL keyword detected: {kw}"

    return True, "Query is safe."


def apply_row_limit(sql: str, limit: int = 100) -> str:
    """Ensure a query has a row limit to prevent excessive data transfer."""
    cleaned = sql.strip().rstrip(";")
    # Check if a LIMIT clause is already present
    if not re.search(r"\bLIMIT\s+\d+\b", cleaned, flags=re.IGNORECASE):
        return f"{cleaned} LIMIT {limit};"
    return f"{cleaned};"


def execute_safe(sql: str, conn_params: dict, timeout_seconds: int = 10) -> dict:
    """Validate and safely execute a query against PostgreSQL."""
    is_safe, reason = validate_sql(sql)
    if not is_safe:
        return {
            "success": False,
            "sql": sql,
            "columns": [],
            "rows": [],
            "error": f"Guardrail blocked query: {reason}",
        }

    safe_sql = apply_row_limit(sql)

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        # Enforce statement timeout
        cur.execute(f"SET statement_timeout = '{int(timeout_seconds * 1000)}ms';")
        cur.execute(safe_sql)

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description] if cur.description else []
        return {
            "success": True,
            "sql": safe_sql,
            "columns": columns,
            "rows": rows,
            "error": None,
        }
    except Exception as e:
        return {
            "success": False,
            "sql": safe_sql,
            "columns": [],
            "rows": [],
            "error": str(e),
        }
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
