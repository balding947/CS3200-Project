import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Spending by Category")
st.write("View spending trends across all students by category.")

try:
    cat_response = requests.get(f"{API_URL}/analytics/spending-by-category").json()
    trend_response = requests.get(f"{API_URL}/analytics/spending-trends").json()
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
    cat_response = []
    trend_response = []

total_all = sum(float(r["total_spent"]) for r in cat_response)

st.subheader("Top Spending Categories")
st.write(f"Total across all expenses: **${total_all:,.2f}**")

if cat_response:
    for row in cat_response:
        pct = (float(row["total_spent"]) / total_all * 100) if total_all > 0 else 0
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.write(f"**{row['category_name']}**")
            st.progress(min(pct / 100, 1.0))
        with col2:
            st.write(f"${float(row['total_spent']):,.2f}")
        with col3:
            st.write(f"{pct:.1f}%")

st.divider()
st.subheader("Monthly Spending Trend")

if trend_response:
    df = pd.DataFrame([
        {"Month": r["month"], "Total Spent": float(r["total_spent"])}
        for r in trend_response
    ])
    st.line_chart(df.set_index("Month"))

if st.button("Back to Home"):
    st.switch_page("pages/30_Rachel_Home.py")