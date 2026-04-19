import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Add a Shared Expense")
st.write("Fill out the form below to log a new shared expense.")

# fetch categories for the dropdown
try:
    categories = requests.get(f"{API_URL}/categories").json()
    category_options = {c["name"]: c["category_id"] for c in categories}
except:
    category_options = {}

# fetch users for the "paid by" dropdown
try:
    users = requests.get(f"{API_URL}/shared-expenses").json()
    # just use a simple list of user ids and names from mock data
    user_options = {
        "Jude (User 7)": 7,
        "Morgan (User 7)": 7,
    }
except:
    user_options = {"Jude (User 7)": 7}

with st.form("add_expense_form"):
    st.subheader("Expense Details")

    name = st.text_input("Expense Name (e.g. Grocery Run)")
    amount = st.number_input("Total Amount ($)", min_value=0.01, step=0.01)
    date = st.date_input("Date")
    category = st.selectbox("Category", options=list(category_options.keys()))

    st.subheader("Split Details")
    split_with = st.multiselect(
        "Split with which roommates?",
        options=["User 5", "User 9", "User 10", "User 11"]
    )
    split_evenly = st.radio("How to split?", ["Split Evenly", "I'll handle it manually"])

    submitted = st.form_submit_button("Save Expense", type="primary")

    if submitted:
        if not name:
            st.error("Please enter an expense name.")
        elif not split_with:
            st.error("Please select at least one roommate to split with.")
        else:
            payload = {
                "name": name,
                "amount": float(amount),
                "date": str(date),
                "paid_by_user_id": 7,
                "category_id": category_options.get(category)
            }
            try:
                response = requests.post(f"{API_URL}/shared-expenses", json=payload)
                if response.status_code == 201:
                    st.success(f"Expense '{name}' added successfully!")
                else:
                    st.error(f"Something went wrong: {response.json().get('error')}")
            except Exception as e:
                st.error(f"Could not connect to the API: {e}")

if st.button("Back to Home"):
    st.switch_page("pages/00_Jude_Home.py")