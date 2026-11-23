# NL-to-SQL Test Questions

Run each through the `/query` endpoint and record results below.

## Test Set

| # | Difficulty | Question | Expected SQL (approx) | Result | Status |
|---|-----------|----------|----------------------|--------|--------|
| 1 | Simple lookup | How many customers are there? | `SELECT COUNT(*) FROM customers;` | | ⬜ |
| 2 | Single join | List all orders placed by customer with ID 5 | `SELECT * FROM orders WHERE customer_id = 5;` | | ⬜ |
| 3 | Two-table join | Which products have less than 10 items in inventory? | `SELECT p.product_name, i.quantity_left FROM products p JOIN inventory i ON p.product_id = i.prod_id WHERE i.quantity_left < 10;` | | ⬜ |
| 4 | Aggregation + join | What are the top 5 products by total revenue? | `SELECT p.product_name, SUM(oi.quantity_bought * oi.price) AS total_revenue FROM products p JOIN order_items oi ON p.product_id = oi.product_id GROUP BY p.product_name ORDER BY total_revenue DESC LIMIT 5;` | | ⬜ |
| 5 | Multi-table aggregation | Which customer spent the most money overall? | `SELECT c.name, SUM(oi.quantity_bought * oi.price) AS total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN order_items oi ON o.order_id = oi.order_id GROUP BY c.customer_id, c.name ORDER BY total_spent DESC LIMIT 1;` | | ⬜ |

## Baseline Accuracy
- Date tested: ___
- Result: ___/5 correct
- Notes: ___

## Failure Log
| Question # | Failure Type | Root Cause | Prompt Fix Applied |
|-----------|-------------|------------|-------------------|
| | | | |
