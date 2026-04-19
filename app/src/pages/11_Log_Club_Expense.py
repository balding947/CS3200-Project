import logging

import requests
import streamlit as st
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Log a Club Expense")
st.write("Record a new expense for your club budget.")

try:
    categories = requests.get(f"{API_URL}/categories").json()
    category_options = {c["name"]: c["category_id"] for c in categories}
except Exception:
    category_options = {}

with st.form("log_club_expense_form"):
    st.subheader("Expense Details")

    description = st.text_area("Description")
    amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
    date = st.date_input("Date")
    category = st.selectbox("Category", options=list(category_options.keys()))
    needs_reimbursement = st.radio("Needs Reimbursement?", ["Yes", "No"])
    notes = st.text_area("Notes (optional)")
    receipt_url = st.text_input("Receipt URL (optional)")

    submitted = st.form_submit_button("Save Expense", type="primary")

    if submitted:
        if not description:
            st.error("Please enter a description.")
        else:
            payload = {
                "description": description,
                "amount": float(amount),
                "date": str(date),
                "needs_reimbursement": 1 if needs_reimbursement == "Yes" else 0,
                "paid_by_user_id": 11,
                "budget_id": 2,
                "category_id": category_options.get(category),
                "notes": notes,
                "receipt_url": receipt_url if receipt_url else None,
            }

            try:
                response = requests.post(f"{API_URL}/club-expenses", json=payload)
                if response.status_code == 201:
                    st.success("Expense logged successfully!")
                else:
                    st.error(f"Something went wrong: {response.json().get('error')}")
            except Exception as e:
                st.error(f"Could not connect to the API: {e}")

if st.button("Back to Home"):
    st.switch_page("pages/10_Daniel_Home.py")