# NL-to-SQL Test Results — Baseline Run

**Date:** 2026-10-22 15:21

## Question 1 — Simple lookup
**Question:** How many customers are there?

**Generated SQL:**
```sql
SELECT COUNT(*) FROM customers;
```

**Columns:** ['count']

**Rows returned:** 1

**Preview (first 3 rows):** `[(100,)]`

**Status:** ✅ Returned results

---

## Question 2 — Single join
**Question:** List all orders placed by customer with ID 5

**Generated SQL:**
```sql
SELECT * FROM orders WHERE customer_id = 5;
```

**Columns:** ['order_id', 'customer_id', 'order_date']

**Rows returned:** 0

**Preview (first 3 rows):** `[]`

**Status:** ✅ Returned results

---

## Question 3 — Two-table join
**Question:** Which products have less than 10 items in inventory?

**Generated SQL:**
```sql
SELECT products.product_name FROM products JOIN inventory ON products.product_id = inventory.prod_id WHERE inventory.quantity_left < 10;
```

**Columns:** ['product_name']

**Rows returned:** 1

**Preview (first 3 rows):** `[('Router',)]`

**Status:** ✅ Returned results

---

## Question 4 — Aggregation + join
**Question:** What are the top 5 products by total revenue?

**Generated SQL:**
```sql
SELECT products.product_name, SUM(order_items.quantity_bought * order_items.price) AS total_revenue FROM products JOIN order_items ON products.product_id = order_items.product_id GROUP BY products.product_id, products.product_name ORDER BY total_revenue DESC LIMIT 5;
```

**Columns:** ['product_name', 'total_revenue']

**Rows returned:** 5

**Preview (first 3 rows):** `[('SSD Drive', Decimal('2136979.73')), ('Standing Desk', Decimal('2084827.85')), ('Monitor', Decimal('1984912.98'))]`

**Status:** ✅ Returned results

---

## Question 5 — Multi-table aggregation
**Question:** Which customer spent the most money overall?

**Generated SQL:**
```sql
SELECT customers.name, SUM(order_items.quantity_bought * order_items.price) AS total_spent FROM customers JOIN orders ON customers.customer_id = orders.customer_id JOIN order_items ON orders.order_id = order_items.order_id GROUP BY customers.customer_id, customers.name ORDER BY total_spent DESC LIMIT 1;
```

**Columns:** ['name', 'total_spent']

**Rows returned:** 1

**Preview (first 3 rows):** `[('Stacey Schwartz', Decimal('1230379.95'))]`

**Status:** ✅ Returned results

---

## Summary
- **Baseline accuracy:** 5/5 returned results
