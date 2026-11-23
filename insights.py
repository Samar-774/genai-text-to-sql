import psycopg2
from llm import get_explanation


def get_low_stock_insight(conn_params: dict) -> dict:
    """Compute low-stock statistics in Python, then ask the LLM to interpret."""
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    # Total number of products
    cur.execute("SELECT COUNT(*) FROM products")
    total_products = cur.fetchone()[0]

    # Products with quantity_left < 10
    cur.execute(
        """
        SELECT p.product_name, i.quantity_left
        FROM products p
        JOIN inventory i ON p.product_id = i.prod_id
        WHERE i.quantity_left < 10
        ORDER BY i.quantity_left ASC
        """
    )
    low_stock_rows = cur.fetchall()
    cur.close()
    conn.close()

    low_stock_count = len(low_stock_rows)
    percentage = round((low_stock_count / total_products) * 100, 2) if total_products else 0
    low_stock_list = [{"product_name": r[0], "quantity_left": r[1]} for r in low_stock_rows]

    product_names = ", ".join(r[0] for r in low_stock_rows) if low_stock_rows else "none"
    prompt = (
        f"{percentage}% of products ({low_stock_count} out of {total_products}) are low stock. "
        f"The low stock products are: [{product_names}]. "
        "Explain what this means for the business in 2-3 sentences."
    )
    llm_explanation = get_explanation(prompt)

    return {
        "stat_name": "Low Stock Products",
        "computed_value": percentage,
        "raw_data": low_stock_list,
        "llm_explanation": llm_explanation,
    }


def get_revenue_concentration_insight(conn_params: dict) -> dict:
    """Compute revenue concentration in Python, then ask the LLM to interpret."""
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    # Total revenue across all products
    cur.execute("SELECT SUM(quantity_bought * price) FROM order_items")
    total_revenue = cur.fetchone()[0] or 0

    # Revenue per product, top first
    cur.execute(
        """
        SELECT p.product_name, SUM(oi.quantity_bought * oi.price) AS product_revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY product_revenue DESC
        """
    )
    revenue_rows = cur.fetchall()
    cur.close()
    conn.close()

    top_product_name = revenue_rows[0][0] if revenue_rows else "N/A"
    top_product_revenue = float(revenue_rows[0][1]) if revenue_rows else 0
    concentration_pct = round((top_product_revenue / float(total_revenue)) * 100, 2) if total_revenue else 0

    prompt = (
        f"The top product '{top_product_name}' accounts for {concentration_pct}% of total revenue "
        f"(${top_product_revenue:,.2f} out of ${float(total_revenue):,.2f}). "
        "Explain what this revenue concentration means for the business in 2-3 sentences."
    )
    llm_explanation = get_explanation(prompt)

    return {
        "stat_name": "Revenue Concentration",
        "computed_value": concentration_pct,
        "raw_data": {
            "total_revenue": float(total_revenue),
            "top_product": top_product_name,
            "top_product_revenue": top_product_revenue,
        },
        "llm_explanation": llm_explanation,
    }


def get_customer_spending_insight(conn_params: dict) -> dict:
    """Compute customer spending stats in Python, then ask the LLM to interpret."""
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    # Spend per customer
    cur.execute(
        """
        SELECT c.name, SUM(oi.quantity_bought * oi.price) AS total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY c.customer_id, c.name
        ORDER BY total_spent DESC
        """
    )
    spending_rows = cur.fetchall()
    cur.close()
    conn.close()

    if spending_rows:
        spends = [float(r[1]) for r in spending_rows]
        avg_spend = round(sum(spends) / len(spends), 2)
        max_spend = max(spends)
        top_customer = spending_rows[0][0]
        ratio = round(max_spend / avg_spend, 2) if avg_spend else 0
    else:
        avg_spend = 0
        max_spend = 0
        top_customer = "N/A"
        ratio = 0

    prompt = (
        f"The average customer spend is ${avg_spend:,.2f} and the top customer '{top_customer}' "
        f"spent ${max_spend:,.2f}, which is {ratio}x the average. "
        "Explain what this spending disparity means for the business in 2-3 sentences."
    )
    llm_explanation = get_explanation(prompt)

    return {
        "stat_name": "Customer Spending Disparity",
        "computed_value": ratio,
        "raw_data": {
            "average_spend": avg_spend,
            "max_spend": max_spend,
            "top_customer": top_customer,
        },
        "llm_explanation": llm_explanation,
    }
