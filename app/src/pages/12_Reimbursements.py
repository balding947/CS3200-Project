import logging

import requests
import streamlit as st
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Track Reimbursements")
st.write("See which club members need to be paid back.")

try:
    response = requests.get(f"{API_URL}/club-expenses?needs_reimbursement=1&budget_id=2")
    expenses = response.json()
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
    expenses = []

if not expenses:
    st.info("No reimbursements needed.")
else:
    st.write(f"Found {len(expenses)} expenses needing reimbursement.")

    for expense in expenses:
        with st.expander(
            f"{expense['description'][:50]} — ${expense['amount']:.2f} on {expense['date']}"
        ):
            st.write(f"**Paid by:** {expense.get('paid_by_name', 'N/A')}")
            st.write(f"**Category:** {expense.get('category_name', 'N/A')}")
            st.write(f"**Notes:** {expense.get('notes', 'N/A')}")

            if expense.get("receipt_url"):
                st.write(f"**Receipt:** [View Receipt]({expense['receipt_url']})")

            try:
                detail = requests.get(
                    f"{API_URL}/club-expenses/{expense['expense_id']}"
                ).json()

                reimbursements = detail.get("reimbursements", [])

                if reimbursements:
                    st.write("**Reimbursement Status:**")
                    for r in reimbursements:
                        status = "Paid" if r["is_paid"] else "Unpaid"
                        col1, col2 = st.columns([4, 2])

                        with col1:
                            st.write(
                                f"{r.get('reimbursed_user_name', 'Unknown')} — "
                                f"${r['amount']:.2f} — {status}"
                            )

                        with col2:
                            if not r["is_paid"]:
                                if st.button("Mark Paid", key=f"reimb_{r['reimb_id']}"):
                                    st.success("Marked as paid!")

            except Exception as e:
                st.error(f"Could not load reimbursement details: {e}")

if st.button("Back to Home"):
    st.switch_page("pages/10_Daniel_Home.py")