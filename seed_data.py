import psycopg2
from faker import Faker
import random
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    database="erp_analytics",
    user="postgres",
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

fake = Faker()

# --- Customers (100 rows) ---
for i in range(1, 101):
    name = fake.name()
    email = fake.email()
    cur.execute(
        "INSERT INTO customers (name, email) VALUES (%s, %s)",
        (name, email)
    )
conn.commit()
print("100 customers inserted successfully")

# --- Products (30 rows) ---
product_list = [
    "Laptop", "Wireless Mouse", "Mechanical Keyboard", "Monitor", "USB-C Hub",
    "External Hard Drive", "Webcam", "Office Chair", "Standing Desk", "Desk Lamp",
    "Printer", "Scanner", "Router", "Headphones", "Bluetooth Speaker",
    "Power Bank", "Laptop Stand", "Cable Organizer", "Surge Protector", "Microphone",
    "Graphics Tablet", "Docking Station", "Ethernet Cable", "SSD Drive", "RAM Module",
    "Cooling Pad", "Wireless Charger", "Smartwatch", "Tablet", "Projector"
]

for i in range(1, 31):
    product_name = product_list[i - 1]
    cur.execute(
        "INSERT INTO products (product_name) VALUES (%s)",
        (product_name,)
    )
conn.commit()
print("30 products inserted successfully")

# --- Inventory (30 rows, one per product) ---
for i in range(1, 31):
    quantity_left = random.randint(0, 200)
    cur.execute(
        "INSERT INTO inventory (prod_id, quantity_left) VALUES (%s, %s)",
        (i, quantity_left)
    )
conn.commit()
print("30 inventory rows inserted successfully")

# --- Orders (200 rows) ---
for i in range(1, 201):
    customer_id = random.randint(1, 100)
    order_date = fake.date_this_year()
    cur.execute(
        "INSERT INTO orders (customer_id, order_date) VALUES (%s, %s)",
        (customer_id, order_date)
    )
conn.commit()
print("200 orders inserted successfully")

# --- Order Items (500 rows) ---
for i in range(1, 501):
    order_id = random.randint(1, 200)
    product_id = random.randint(1, 30)
    quantity_bought = random.randint(1, 5)
    price = round(random.uniform(100, 50000), 2)
    cur.execute(
        "INSERT INTO order_items (order_id, product_id, quantity_bought, price) VALUES (%s, %s, %s, %s)",
        (order_id, product_id, quantity_bought, price)
    )
conn.commit()
print("500 order items inserted successfully")

# --- Cleanup ---
cur.close()
conn.close()
print("All data seeded successfully.")
