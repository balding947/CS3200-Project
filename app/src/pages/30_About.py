import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# About this App")

st.markdown(
    """
    This is a demo financial management app for college students built for a database course.  

    The goal of this app is to showcase features such as shared expense tracking, club budget management, 
    and viewing financial analytics through a dashboard. It demonstrates how users can log expenses, 
    split costs, manage categories, and monitor payments, while also supporting administrators with summarized 
    insights and reporting tools.

    Stay tuned for more information and features to come!
    """
)

# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
