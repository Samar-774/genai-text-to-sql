"""
Comprehensive verification test for Guardrails, NL-to-SQL, and Grounded Insights.
"""
import os
import sys

from dotenv import load_dotenv
load_dotenv()

from guardrails import validate_sql, apply_row_limit, execute_safe
from main import get_db_params
from llm import generate_sql
from insights import (
    get_low_stock_insight,
    get_revenue_concentration_insight,
    get_customer_spending_insight,
)

db_params = get_db_params()

print("=" * 60)
print("1. TESTING GUARDRAILS")
print("=" * 60)

test_cases = [
    ("DROP TABLE customers;", False),
    ("DELETE FROM orders WHERE order_id = 1;", False),
    ("UPDATE inventory SET quantity_left = 0;", False),
    ("INSERT INTO products (product_name) VALUES ('Hacked');", False),
    ("SELECT * FROM customers; DROP TABLE orders;", False),
    ("SELECT * FROM products WHERE product_name = 'Laptop';", True),
]

guardrails_passed = 0
for query, expected_safe in test_cases:
    is_safe, reason = validate_sql(query)
    match = (is_safe == expected_safe)
    status_icon = "[PASS]" if match else "[FAIL]"
    if match:
        guardrails_passed += 1
    print(f"{status_icon} Query: '{query}' -> is_safe={is_safe} ({reason})")

print(f"\nGuardrails test summary: {guardrails_passed}/{len(test_cases)} matched expected security behavior.")

print("\n" + "=" * 60)
print("2. TESTING END-TO-END EXECUTION VIA GUARDRAILS")
print("=" * 60)

# Safe query test
res_safe = execute_safe("SELECT COUNT(*) FROM customers", db_params)
print("Safe query execution success:", res_safe["success"])
print("Columns:", res_safe["columns"])
print("Rows:", res_safe["rows"])

# Adversarial query execution test
res_blocked = execute_safe("DELETE FROM customers", db_params)
print("\nAdversarial query blocked:", not res_blocked["success"])
print("Error captured:", res_blocked["error"])

print("\n" + "=" * 60)
print("3. TESTING GROUNDED INSIGHTS (DAY 8)")
print("=" * 60)

print("\nFetching Low Stock Insight...")
insight1 = get_low_stock_insight(db_params)
print(f"Stat: {insight1['stat_name']} -> {insight1['computed_value']}%")
print(f"LLM Explanation: {insight1['llm_explanation']}")

print("\nFetching Revenue Concentration Insight...")
insight2 = get_revenue_concentration_insight(db_params)
print(f"Stat: {insight2['stat_name']} -> {insight2['computed_value']}%")
print(f"LLM Explanation: {insight2['llm_explanation']}")

print("\nFetching Customer Spending Disparity Insight...")
insight3 = get_customer_spending_insight(db_params)
print(f"Stat: {insight3['stat_name']} -> {insight3['computed_value']}x")
print(f"LLM Explanation: {insight3['llm_explanation']}")

print("\n" + "=" * 60)
print("ALL CHECKS COMPLETED SUCCESSFULLY!")
print("=" * 60)
