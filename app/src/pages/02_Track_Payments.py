import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Track Payments")
st.write("See who has and hasn't paid you back for shared expenses.")

try:
    response = requests.get(f"{API_URL}/shared-expenses?paid_by_user_id=7")
    expenses = response.json()
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
    expenses = []

if not expenses:
    st.info("No shared expenses found.")
else:
    for expense in expenses:
        with st.expander(f"{expense['name']} — ${expense['amount']:.2f} on {expense['date']}"):
            st.write(f"**Category:** {expense.get('category_name', 'N/A')}")

            try:
                detail = requests.get(f"{API_URL}/shared-expenses/{expense['expense_id']}").json()
                splits = detail.get("splits", [])

                if splits:
                    st.write("**Split Status:**")
                    for split in splits:
                        status = "Paid" if split["is_paid"] else "Unpaid"
                        col1, col2, col3 = st.columns([3, 2, 2])
                        with col1:
                            st.write(f"{split['roommate_name']}")
                        with col2:
                            st.write(f"${split['amount_owed']:.2f} — {status}")
                        with col3:
                            if not split["is_paid"]:
                                if st.button("Mark Paid", key=f"pay_{split['split_id']}"):
                                    update = requests.put(
                                        f"{API_URL}/shared-expenses/update/{expense['expense_id']}",
                                        json={"is_paid": 1}
                                    )
                                    st.success("Marked as paid!")
                                    st.rerun()
                else:
                    st.info("No splits recorded for this expense.")

            except Exception as e:
                st.error(f"Could not load split details: {e}")

            if st.button("Delete this expense", key=f"del_{expense['expense_id']}"):
                delete = requests.delete(
                    f"{API_URL}/shared-expenses/delete/{expense['expense_id']}"
                )
                if delete.status_code == 200:
                    st.success("Expense deleted!")
                    st.rerun()
                else:
                    st.error("Could not delete expense.")

if st.button("Back to Home"):
    st.switch_page("pages/00_Jude_Home.py")