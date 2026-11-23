# ERP GenAI Analytics & SQL Agent

An enterprise Text-to-SQL and grounded business intelligence platform built over an ERP relational schema. Allows business users to ask natural language questions, inspect generated SQL queries, and receive statistically grounded strategic insights with guardrails preventing unauthorized data mutation.

🔗 **Live Demo**: [https://genai-text-to-sql.streamlit.app](https://genai-text-to-sql.streamlit.app)

---

## 🏗 Architecture Overview

```
Business User (Browser)
       │
       ▼
Streamlit Frontend (`dashboard.py`)
  ├── Natural Language Query Input & Sample Prompts
  ├── Generated SQL Inspection & Interactive Result DataFrames
  └── Grounded Business Insights Dashboard
       │
       ▼ (HTTP REST)
FastAPI Backend (`main.py`)
  ├── /ping      -> Healthcheck & DB row count confirmation
  ├── /query     -> Natural Language to SQL + Guardrails execution
  └── /insights  -> Python-computed metrics with LLM interpretation
       │
       ├── Google Gemini API (`llm.py`)
       │     ├── Few-shot SQL Generation (`gemini-3.6-flash`)
       │     └── Analytical Business Explanations
       │
       ├── Guardrails Layer (`guardrails.py`)
       │     ├── Strict AST/Keyword Check (SELECT / WITH only)
       │     ├── Mutation & Injection Defense (blocks DROP, DELETE, etc.)
       │     ├── Automatic Row Limit Enforcement (LIMIT 100)
       │     └── Query Timeout Enforcement (PostgreSQL statement_timeout)
       │
       └── PostgreSQL Database (`erp_analytics`)
             ├── customers (100 rows)
             ├── products (30 rows)
             ├── inventory (30 rows)
             ├── orders (200 rows)
             └── order_items (500 rows)
```

---

## 🚀 Key Features

### 1. Natural Language to SQL
- Translates conversational questions into PostgreSQL queries using few-shot prompt engineering.
- Returns the generated SQL query, raw result table, and column headers.

### 2. Multi-Layer SQL Guardrails (`guardrails.py`)
- **Strict Read-Only Enforcement**: Rejects non-`SELECT`/`WITH` statements.
- **Destructive Query Defense**: Regex token matching detects and rejects dangerous keywords (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`, `ALTER`, `GRANT`, `REVOKE`).
- **SQL Injection Prevention**: Blocks multi-statement execution containing semicolons.
- **Runaway Query Protection**: Automatically appends `LIMIT 100` if no limit is specified and enforces a 10-second `statement_timeout`.

### 3. Grounded Business Insights (`insights.py`)
Avoids hallucinated metrics by separating computation from narration:
1. **Deterministic Computation (Python + SQL)**: Accurately calculates low-stock percentages, revenue concentration, and spending disparities directly from the database.
2. **Contextual Narration (LLM)**: Passes the trusted numbers to the model strictly for executive interpretation and business context.

---

## 📊 Database Schema (ERP Dataset)

The project models an ERP analytics domain inspired by enterprise supply-chain and order-management architectures:

1. **`customers`**: Customer master table (`customer_id`, `name`, `email`).
2. **`products`**: Product catalog (`product_id`, `product_name`).
3. **`inventory`**: Real-time stock levels (`prod_id` PK/FK, `quantity_left`).
4. **`orders`**: Transaction header (`order_id`, `customer_id` FK, `order_date`).
5. **`order_items`**: Line items per order (`order_item_id`, `order_id` FK, `product_id` FK, `quantity_bought`, `price`).

---

## 🧪 Measured Accuracy & Test Baseline

Tested against a 5-question baseline of varying complexity:

| # | Question Complexity | Query Target | Status |
|---|---------------------|--------------|--------|
| 1 | Simple lookup | `SELECT COUNT(*) FROM customers` | ✅ Correct (100 rows) |
| 2 | Filter with ID | `SELECT * FROM orders WHERE customer_id = 5` | ✅ Correct SQL |
| 3 | Two-table JOIN + WHERE | Low stock products (`quantity_left < 10`) | ✅ Correct |
| 4 | Aggregation + JOIN + ORDER BY | Top 5 products by revenue | ✅ Correct |
| 5 | Three-table JOIN + Aggregation | Top customer by total spend | ✅ Correct |

**Overall Baseline Accuracy**: 5 / 5 (100% on standard ERP queries).

---

## ☁️ Deployment

| Layer | Platform |
|-------|----------|
| Frontend | Streamlit Cloud |
| Backend API | Render |
| Database | Neon (Serverless PostgreSQL) |

---

## 🛠 Local Setup & Installation

### Prerequisites
- Python 3.11+
- PostgreSQL installed locally (or via Docker)

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-username/genai-sql-project.git
cd genai-sql-project

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```
```ini
DATABASE_URL=your_neon_connection_string
GEMINI_API_KEY=your_gemini_api_key
DB_PASSWORD=your_local_postgres_password  # fallback for local dev only
```

### 3. Initialize Database & Seed Synthetic Data
```bash
# Seed tables with 100 customers, 30 products, 200 orders, 500 line items:
python seed_data.py
```

### 4. Run the Backend API
```bash
uvicorn main:app --reload --port 8000
```
API Documentation will be live at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 5. Run the Streamlit Frontend
In a separate terminal:
```bash
streamlit run dashboard.py
```
App will open at: [http://localhost:8501](http://localhost:8501)

---

## 🔒 Known Limitations & Trade-Offs

- **Synthetic Price Variations**: Pricing in synthetic data is generated uniformly per line item rather than bound to a static catalog price list.
- **Postgres Dialect**: Prompt schema and guardrails are tailored specifically for PostgreSQL syntax and type conventions.
- **Single-Turn Interaction**: The current pipeline processes standalone queries without carrying conversational query state across turns.
- **Cold Start**: The Render free tier may take 30–50 seconds to wake up after inactivity. The first query after a long idle period will be slower.