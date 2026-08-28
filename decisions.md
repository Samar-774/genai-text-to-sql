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
- Day 2: not started. Next up — minimal FastAPI endpoint, hardcoded SQL query, one LLM call for explanation, bare-bones Streamlit UI. "Prove the plumbing" day, no AI-generated SQL yet.