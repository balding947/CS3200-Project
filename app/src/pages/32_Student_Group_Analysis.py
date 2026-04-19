import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Student Group Analysis")
st.write("Filter spending data by student group to identify trends.")

housing_types = ["All", "off-campus apartment", "traditional dorm",
                 "on-campus apartment", "suite-style dorm", "commuter"]
class_years = ["All", "2026", "2027", "2028", "2029"]

col1, col2 = st.columns(2)
with col1:
    selected_housing = st.selectbox("Filter by Housing Type", housing_types)
with col2:
    selected_year = st.selectbox("Filter by Class Year", class_years)

params = {}
if selected_housing != "All":
    params["housing_type"] = selected_housing
if selected_year != "All":
    params["class_year"] = selected_year

try:
    response = requests.get(f"{API_URL}/analytics/student-group-spending", params=params)
    data = response.json()
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
    data = []

st.divider()

if not data:
    st.info("No data found for the selected filters.")
else:
    total_spent = sum(float(r["total_spent"]) for r in data)
    total_expenses = len(data)
    avg = total_spent / total_expenses if total_expenses > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Categories", total_expenses)
    with col2:
        st.metric("Total Spent", f"${total_spent:,.2f}")
    with col3:
        st.metric("Average per Category", f"${avg:,.2f}")

    st.subheader("Spending by Category")
    most_common = max(data, key=lambda x: float(x["total_spent"]))
    st.write(f"**Highest spending category:** {most_common['category_name']} (${float(most_common['total_spent']):,.2f})")

    df = pd.DataFrame([
        {"Category": r["category_name"], "Total Spent": float(r["total_spent"])}
        for r in data
    ])
    df = df.groupby("Category")["Total Spent"].sum().reset_index()
    df = df.sort_values("Total Spent", ascending=False)
    st.bar_chart(df.set_index("Category"))

    st.subheader("Breakdown by Housing Type and Class Year")
    for row in data:
        st.write(f"- **{row['housing_type']}** (Class of {row['class_year']}) — "
                 f"{row['category_name']}: ${float(row['total_spent']):,.2f}")

if st.button("Back to Home"):
    st.switch_page("pages/30_Rachel_Home.py")