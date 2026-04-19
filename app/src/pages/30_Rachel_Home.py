import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}!")
st.write('### What would you like to do today?')

if st.button('View Spending by Category',
             type='primary', use_container_width=True):
    st.switch_page('pages/31_Spending_By_Category.py')

if st.button('Analyze Student Groups',
             type='primary', use_container_width=True):
    st.switch_page('pages/32_Student_Group_Analysis.py')

if st.button('Manage Dashboard Filters',
             type='primary', use_container_width=True):
    st.switch_page('pages/33_Dashboard_Filters.py')