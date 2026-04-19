import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Expense History")
st.write("Browse and edit all shared apartment expenses.")

# filters
col1, col2 = st.columns(2)
with col1:
    filter_category = st.selectbox(
        "Filter by Category",
        options=["All"] + [c["name"] for c in requests.get(f"{API_URL}/categories").json()]
    )
with col2:
    filter_payer = st.selectbox(
        "Filter by Payer",
        options=["All", "Paid by me (Jude)"]
    )

# build query params
params = {}
if filter_payer == "Paid by me (Jude)":
    params["paid_by_user_id"] = 7
if filter_category != "All":
    categories = requests.get(f"{API_URL}/categories").json()
    cat_id = next((c["category_id"] for c in categories if c["name"] == filter_category), None)
    if cat_id:
        params["category_id"] = cat_id

try:
    response = requests.get(f"{API_URL}/shared-expenses", params=params)
    expenses = response.json()
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
    expenses = []

st.write(f"Showing {len(expenses)} expenses")

for expense in expenses:
    with st.expander(f"{expense['name']} — ${expense['amount']:.2f} on {expense['date']}"):
        st.write(f"**Paid by:** {expense['paid_by_name']}")
        st.write(f"**Category:** {expense.get('category_name', 'N/A')}")

        with st.form(key=f"edit_{expense['expense_id']}"):
            st.write("**Edit this expense:**")
            new_name = st.text_input("Name", value=expense["name"])
            new_amount = st.number_input("Amount", value=float(expense["amount"]), min_value=0.01, step=0.01)
            save = st.form_submit_button("Save Changes")

            if save:
                try:
                    update = requests.put(
                        f"{API_URL}/shared-expenses/update/{expense['expense_id']}",
                        json={"name": new_name, "amount": new_amount}
                    )
                    if update.status_code == 200:
                        st.success("Expense updated!")
                        st.rerun()
                    else:
                        st.error("Could not update expense.")
                except Exception as e:
                    st.error(f"Error: {e}")

if st.button("Back to Home"):
    st.switch_page("pages/00_Jude_Home.py")