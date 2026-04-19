import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}!")
st.write('### What would you like to do today?')

if st.button('Add a Shared Expense',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/01_Add_Expense.py')

if st.button('Track Who Has Paid',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/02_Track_Payments.py')

if st.button('View Expense History',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/03_Expense_History.py')