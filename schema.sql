CREATE TABLE customers(
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE
);

CREATE TABLE products(
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(50) NOT NULL
);

CREATE TABLE inventory(
    prod_id INT REFERENCES products(product_id) PRIMARY KEY,
    quantity_left INT NOT NULL
);

CREATE TABLE orders(
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date DATE NOT NULL
);

CREATE TABLE order_items(
    order_item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity_bought INT NOT NULL,
    price NUMERIC(10,2) NOT NULL
);