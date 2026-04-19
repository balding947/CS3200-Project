import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Flagged Transactions")
st.write("Review and resolve flagged expenses.")

try:
    shared = requests.get(f"{API_URL}/shared-expenses").json()
except:
    shared = []

try:
    club = requests.get(f"{API_URL}/club-expenses").json()
except:
    club = []

tab1, tab2 = st.tabs(["Shared Expense Flags", "Club Expense Flags"])

with tab1:
    st.subheader("Flagged Shared Expenses")
    flagged_shared_ids = [43, 28, 9, 29, 6, 58, 34, 54, 36, 14]
    flagged_shared = [e for e in shared if e["expense_id"] in flagged_shared_ids]
    if not flagged_shared:
        st.info("No flagged shared expenses.")
    else:
        for expense in flagged_shared:
            with st.expander(
                f"{expense['name']} — ${expense['amount']:.2f} on {expense['date']}"
            ):
                st.write(f"**Paid by:** {expense.get('paid_by_name', 'N/A')}")
                st.write(f"**Category:** {expense.get('category_name', 'N/A')}")
                with st.form(key=f"flag_shared_{expense['expense_id']}"):
                    new_name = st.text_input("Name", value=expense["name"])
                    new_amount = st.number_input(
                        "Amount", value=float(expense["amount"]), min_value=0.01
                    )
                    save = st.form_submit_button("Update Record")
                    if save:
                        try:
                            r = requests.put(
                                f"{API_URL}/shared-expenses/update/{expense['expense_id']}",
                                json={"name": new_name, "amount": new_amount}
                            )
                            if r.status_code == 200:
                                st.success("Record updated!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

with tab2:
    st.subheader("Flagged Club Expenses")
    flagged_club_ids = [28, 52, 51, 41, 45, 30, 11, 24, 43, 55]
    flagged_club = [e for e in club if e["expense_id"] in flagged_club_ids]
    if not flagged_club:
        st.info("No flagged club expenses.")
    else:
        for expense in flagged_club:
            with st.expander(
                f"{expense['description'][:50]} — ${expense['amount']:.2f}"
            ):
                st.write(f"**Paid by:** {expense.get('paid_by_name', 'N/A')}")
                st.write(f"**Category:** {expense.get('category_name', 'N/A')}")
                st.write(f"**Notes:** {expense.get('notes', 'N/A')}")
                with st.form(key=f"flag_club_{expense['expense_id']}"):
                    new_desc = st.text_area(
                        "Description", value=expense.get("description", "")
                    )
                    new_amount = st.number_input(
                        "Amount", value=float(expense["amount"]), min_value=0.01
                    )
                    save = st.form_submit_button("Update Record")
                    if save:
                        try:
                            r = requests.put(
                                f"{API_URL}/club-expenses/update/{expense['expense_id']}",
                                json={"description": new_desc, "amount": new_amount}
                            )
                            if r.status_code == 200:
                                st.success("Record updated!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

if st.button("Back to Home"):
    st.switch_page("pages/20_Sofia_Home.py")
