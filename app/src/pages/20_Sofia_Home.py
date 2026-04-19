import logging
logger = logging.getLogger(__name__)
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}!")
st.write('### What would you like to do today?')

if st.button('Manage Categories',
             type='primary', use_container_width=True):
    st.switch_page('pages/21_Manage_Categories.py')

if st.button('Review Flagged Transactions',
             type='primary', use_container_width=True):
    st.switch_page('pages/22_Flagged_Transactions.py')

if st.button('View Support Issues',
             type='primary', use_container_width=True):
    st.switch_page('pages/23_Support_Issues.py')
