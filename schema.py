SCHEMA = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100) UNIQUE
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(50) NOT NULL
);

CREATE TABLE inventory (
    prod_id INTEGER PRIMARY KEY REFERENCES products(product_id),
    quantity_left INTEGER NOT NULL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE NOT NULL
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity_bought INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL
);
"""