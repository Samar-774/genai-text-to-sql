# Project Decisions Log
Keep this updated as you go. Paste it into any new chat alongside the roadmap file so nothing gets lost.

## Schema
- 5 tables (roadmap suggested 4–5 minimum, went with 5): `customers`, `products`, `inventory`, `orders`, `order_items`
- `orders` and `order_items` are split (not one table) — an order can contain multiple products, so one row per order can't hold all line items. Classic one-to-many pattern.
- `price` lives in `order_items`, not `products` — price at time of purchase should stay fixed even if the product's price changes later.
- `quantity_left` lives in its own `inventory` table, not in `products` — stock changes over time, same reasoning as price.
- `inventory.prod_id` is both PK and FK — valid because there's exactly one inventory row per product (no per-warehouse split in this scope).
- `order_items.order_item_id` is its own PK (not `order_id`) — because `order_id` alone repeats across multiple rows (one order, multiple items), so it can't uniquely identify a row.
- `product_name` is NOT unique — two products can share a name (e.g. different models both called similar things).
- Product names are a hardcoded list of 30 distinct items (not Faker-generated) — Faker has no realistic "product name" generator, and distinct names make later insight queries (e.g. "top-selling product") meaningful.
- Price is fully random per order_item, not tied to which product it is — deliberate scope simplification, since the project's focus is NL-to-SQL quality, not realistic pricing. Explainable in interview as an intentional trade-off.

## Row counts (seeded)
- customers: 100
- products: 30
- inventory: 30 (one per product)
- orders: 200
- order_items: 500 (~2.5 items per order average)

## Environment
- Local Postgres install on Windows (not Docker) — chosen for faster dev iteration, avoiding Docker startup overhead.
- Python venv (`venv`) inside project folder, used alongside Conda base (venv takes priority — confirmed via `Get-Command python`).
- Libraries: `faker`, `psycopg2-binary`.
- Seed script: `seed_data.py`, run once end-to-end, inserts in FK-safe order: customers → products → inventory → orders → order_items.

## 📌 Day 9 deployment note (do not forget)
- Local dev uses local Postgres. Deployment will use a **separate managed Postgres** (Neon / Supabase / Render free tier).
- `seed_data.py` will need to be **re-run against the hosted DB**, not just local — same script, different connection target.
- Planned deploy: FastAPI + Streamlit deployed separately (Render/Railway for backend, Streamlit Community Cloud for frontend) — avoids Docker entirely end-to-end, matching the "avoid Docker overhead" choice made in dev.

## Resume / timeline context
- Resume already submitted with an "in progress" bullet — not claiming completion.
- GitHub link already on resume; demo link will be added to README once deployed.
- Real interview ~10 days out from submission. Working ~1–3 hrs/day around DSA/CS fundamentals revision.

## Status
- Day 1: COMPLETE. Schema designed, live in Postgres, fully seeded, verified with a hand-written 3+ table JOIN (order_items → orders → customers, + products).
- Day 2: COMPLETE. FastAPI + Postgres + Gemini + Streamlit, full chain working end-to-end.
  - LLM provider decision: Gemini API (free tier), model `gemini-3.6-flash`.
  - Bug hit: occasional `503 UNAVAILABLE` from Gemini under high demand — transient, not a code issue.
  - Prompt lesson learned: a prompt needs an explicit instruction/command, not just stated facts — otherwise the model either asks what to do, or over-produces (headers/bullets) with no length constraint given.
  - File structure: `main.py` (FastAPI + Postgres), `llm.py` (Gemini call), `dashboard.py` (Streamlit).
  - Known issue to fix on Day 3: prompt doesn't yet constrain output length — currently produces good short paragraphs sometimes, longer multi-section answers other times.


- Day 3: COMPLETE. NL-to-SQL first pass working.
  - `generate_sql()` in `llm.py` uses DDL-format schema from `schema.py` + 2 few-shot examples.
  - `/query` endpoint in `main.py` accepts `?q=` param, returns generated SQL + columns + rows.
  - `schema_description.py` completed with all 4 FK relationships spelled out.
  - Known issue: LLM sometimes wraps SQL in markdown fences — needs stripping.
- Day 4: COMPLETE. Few-shot prompting added (2 examples: inventory lookup + top customers by spend).
  - Baseline test run: **5/5 questions produced correct SQL**.
  - Q1 (simple count): ✅ correct
  - Q2 (filter by customer_id): ✅ correct SQL, 0 rows (no orders for customer_id=5 in random data — data issue, not SQL issue)
  - Q3 (two-table join + WHERE): ✅ correct
  - Q4 (aggregation + join + ORDER BY + LIMIT): ✅ correct
  - Q5 (3-table join + aggregation): ✅ correct
  - Full results logged in `test_results.md`.
- Days 5–6: COMPLETE. No systematic failures to debug at 5/5 baseline. Prompt structure locked.
  - Accuracy: 5/5 correct SQL on test set.
  - Remaining improvements: markdown fence stripping, guardrails, error handling.
- Day 7: IN PROGRESS. Guardrails implementation.
  - `guardrails.py` — SQL validation (SELECT-only allowlist), row limit, query timeout, safe execution wrapper.
  - `llm.py` — `sanitize_sql()` to strip markdown fences from LLM output.
- Day 8: IN PROGRESS. Grounded insights.
  - `insights.py` — compute real statistics in Python, hand trusted numbers to LLM for interpretation.
  - `/insights` endpoint added to `main.py`.

- Day 9: COMPLETE. Streamlit UI overhauled in `dashboard.py`.
  - Tab 1: Natural Language SQL Explorer with sample query buttons, generated SQL display in collapsible expander, results DataFrame, row count, and guardrail error alerts.
  - Tab 2: Grounded Business Insights displaying real-time metrics cards and detailed analytical narratives from `/insights`.
- Day 10: COMPLETE. Verified entire end-to-end flow with automated test suite in `verify_pipeline.py`. 6/6 guardrail tests passed. Safe and adversarial queries verified.
- Days 11-12: COMPLETE.
  - Pinned `requirements.txt` generated.
  - `README.md` authored detailing architecture, guardrail defenses, grounded insights design, baseline accuracy, and local run instructions.
