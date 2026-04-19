import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Spending by Category")
st.write("View spending trends across all students by category.")

try:
    shared = requests.get(f"{API_URL}/shared-expenses").json()
    club = requests.get(f"{API_URL}/club-expenses").json()
    categories = requests.get(f"{API_URL}/categories").json()
    cat_names = {c["category_id"]: c["name"] for c in categories}
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
    shared = []
    club = []
    cat_names = {}

category_totals = {}
for e in shared:
    cat = cat_names.get(e.get("category_id"), "Uncategorized")
    category_totals[cat] = category_totals.get(cat, 0) + float(e["amount"])
for e in club:
    cat = cat_names.get(e.get("category_id"), "Uncategorized")
    category_totals[cat] = category_totals.get(cat, 0) + float(e["amount"])

sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
total_all = sum(category_totals.values())

st.subheader("Top Spending Categories")
st.write(f"Total across all expenses: **${total_all:,.2f}**")

for cat, total in sorted_cats:
    pct = (total / total_all * 100) if total_all > 0 else 0
    col1, col2, col3 = st.columns([4, 2, 1])
    with col1:
        st.write(f"**{cat}**")
        st.progress(min(pct / 100, 1.0))
    with col2:
        st.write(f"${total:,.2f}")
    with col3:
        st.write(f"{pct:.1f}%")

st.divider()
st.subheader("Monthly Spending Trend")

monthly = {}
for e in shared:
    month = e["date"][:7]
    monthly[month] = monthly.get(month, 0) + float(e["amount"])
for e in club:
    month = e["date"][:7]
    monthly[month] = monthly.get(month, 0) + float(e["amount"])

sorted_monthly = sorted(monthly.items())
if sorted_monthly:
    import pandas as pd
    df = pd.DataFrame(sorted_monthly, columns=["Month", "Total Spent"])
    st.line_chart(df.set_index("Month"))

if st.button("Back to Home"):
    st.switch_page("pages/30_Rachel_Home.py")