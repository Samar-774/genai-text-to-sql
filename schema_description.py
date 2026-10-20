SCHEMA = """
You have access to a PostgreSQL database with the following tables:

Table: customers
Columns: customer_id (INTEGER, PK), name (VARCHAR), email (VARCHAR UNIQUE)

Table: products
Columns: product_id (INTEGER, PK), product_name (VARCHAR)

Table: inventory
Columns: prod_id (INTEGER, PK, FK→products.product_id), quantity_left (INTEGER)

Table: orders
Columns: order_id (INTEGER, PK), customer_id (INTEGER, FK→customers.customer_id), order_date (DATE)

Table: order_items
Columns: order_item_id (INTEGER, PK), order_id (INTEGER, FK→orders.order_id), product_id (INTEGER, FK→products.product_id), quantity_bought (INTEGER), price (NUMERIC)

Relationships:
- ...  ← you fill this in
"""