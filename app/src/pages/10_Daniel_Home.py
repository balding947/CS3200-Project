import logging

import streamlit as st
from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}!")
st.write("### What would you like to do today?")

if st.button("Log a Club Expense", type="primary", use_container_width=True):
    st.switch_page("pages/11_Log_Club_Expense.py")

if st.button("Track Reimbursements", type="primary", use_container_width=True):
    st.switch_page("pages/12_Reimbursements.py")

if st.button("View Budget Summary", type="primary", use_container_width=True):
    st.switch_page("pages/13_Budget_Summary.py")