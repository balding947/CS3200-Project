import logging

import requests
import streamlit as st
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Budget Summary")
st.write("See how much of your club budget has been used.")

try:
    response = requests.get(f"{API_URL}/club-expenses?budget_id=2")
    expenses = response.json()
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
    expenses = []

total_budget = 7536.00
total_spent = sum(float(e["amount"]) for e in expenses)
remaining = total_budget - total_spent
pct_used = (total_spent / total_budget) * 100 if total_budget > 0 else 0

st.subheader("Asian Student Association Fall 2025 Activities Fund")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Budget", f"${total_budget:,.2f}")
with col2:
    st.metric("Amount Spent", f"${total_spent:,.2f}")
with col3:
    st.metric("Remaining", f"${remaining:,.2f}")

st.progress(min(pct_used / 100, 1.0))
st.write(f"{pct_used:.1f}% of budget used")

st.subheader("Spending by Category")
category_totals = {}
for e in expenses:
    cat = e.get("category_name") or "Uncategorized"
    category_totals[cat] = category_totals.get(cat, 0) + float(e["amount"])

for cat, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(f"**{cat}**")
        st.progress(min(total / total_budget, 1.0))
    with col2:
        st.write(f"${total:,.2f}")

st.subheader("Recent Expenses")
for expense in expenses[:5]:
    st.write(
        f"- {expense['description'][:50]} — "
        f"${expense['amount']:.2f} on {expense['date']}"
    )

if st.button("Back to Home"):
    st.switch_page("pages/10_Daniel_Home.py")