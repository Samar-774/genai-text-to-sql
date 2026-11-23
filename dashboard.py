import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "https://genai-text-to-sql-v0tm.onrender.com"

st.set_page_config(
    page_title="ERP GenAI Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 ERP GenAI Analytics & SQL Agent")
st.caption("Ask natural language business questions over your ERP database with automated SQL generation, safe guardrails, and grounded insights.")

tab_query, tab_insights = st.tabs(["💬 Ask Questions (Text-to-SQL)", "📈 Grounded Business Insights"])

with tab_query:
    st.subheader("Natural Language Database Query")
    
    # Suggested queries for quick exploration
    st.markdown("**Quick sample prompts:**")
    col1, col2, col3 = st.columns(3)
    if "query_input" not in st.session_state:
        st.session_state.query_input = ""

    if col1.button("📦 Which products are low on inventory (<10)?", use_container_width=True):
        st.session_state.query_input = "Which products have less than 10 items in inventory?"
    if col2.button("🏆 Top 5 products by revenue", use_container_width=True):
        st.session_state.query_input = "What are the top 5 products by total revenue?"
    if col3.button("💰 Top customer by total spend", use_container_width=True):
        st.session_state.query_input = "Which customer spent the most money overall?"

    query_input = st.text_input(
        "Enter your question in plain English:",
        value=st.session_state.query_input,
        placeholder="e.g. How many customers are there in the database?"
    )

    if st.button("🚀 Run Query", type="primary"):
        if not query_input.strip():
            st.warning("Please type a question or select a sample query above.")
        else:
            with st.spinner("Generating SQL and querying database..."):
                try:
                    resp = requests.get(f"{API_BASE_URL}/query", params={"q": query_input}, timeout=60)
                    data = resp.json()
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ Could not connect to FastAPI server at `127.0.0.1:8000`. Make sure the backend is running (`uvicorn main:app --reload`).")
                    data = None
                except Exception as e:
                    st.error(f"Request failed: {e}")
                    data = None

            if data:
                if data.get("error"):
                    st.error(f"🛑 Query Blocked or Failed:\n\n{data['error']}")
                    if data.get("sql"):
                        with st.expander("Inspected SQL"):
                            st.code(data["sql"], language="sql")
                else:
                    st.success("Query executed successfully!")
                    
                    # Display generated SQL
                    with st.expander("🔍 View Generated SQL", expanded=True):
                        st.code(data["sql"], language="sql")
                    
                    columns = data.get("columns", [])
                    rows = data.get("rows", [])
                    
                    if rows:
                        df = pd.DataFrame(rows, columns=columns)
                        st.dataframe(df, use_container_width=True)
                        st.caption(f"Showing {len(df)} row(s). Row limit auto-enforced by guardrails.")
                    else:
                        st.info("Query returned 0 rows.")

with tab_insights:
    st.subheader("Grounded Business Metrics")
    st.caption("These insights are computed deterministically in Python first, then handed to the LLM for business interpretation.")

    if st.button("🔄 Refresh Grounded Insights"):
        with st.spinner("Computing statistics and generating insights..."):
            try:
                resp = requests.get(f"{API_BASE_URL}/insights", timeout=60)
                if resp.status_code == 200:
                    insights_data = resp.json().get("insights", [])
                    st.session_state["insights_data"] = insights_data
                else:
                    st.error(f"Backend returned error code: {resp.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("⚠️ Backend server not reachable at `http://127.0.0.1:8000`. Please start it first.")
            except Exception as e:
                st.error(f"Error fetching insights: {e}")

    # Display cached or newly fetched insights
    cached_insights = st.session_state.get("insights_data")
    if cached_insights:
        c1, c2, c3 = st.columns(3)
        for idx, insight in enumerate(cached_insights):
            col = [c1, c2, c3][idx % 3]
            with col:
                st.metric(
                    label=insight.get("stat_name", "Insight"),
                    value=f"{insight.get('computed_value')}%" if "Concentration" in insight.get("stat_name", "") or "Stock" in insight.get("stat_name", "") else f"{insight.get('computed_value')}x"
                )

        st.divider()
        for insight in cached_insights:
            with st.expander(f"📌 {insight.get('stat_name')} — Analysis", expanded=True):
                st.markdown(f"**Interpretation:** {insight.get('llm_explanation')}")
                st.json(insight.get("raw_data"))
    else:
        st.info("Click 'Refresh Grounded Insights' above to calculate real-time analytics across inventory, revenue, and customer spending.")
