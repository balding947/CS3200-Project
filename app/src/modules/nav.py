# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st


# ---- General ----------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


# ---- Role: jude -------------------------------------------------------------

def jude_home_nav():
    st.sidebar.page_link("pages/00_Jude_Home.py", label="Jude's Home", icon="🏠")

def add_expense_nav():
    st.sidebar.page_link("pages/01_Add_Expense.py", label="Add Shared Expense", icon="➕")

def track_payments_nav():
    st.sidebar.page_link("pages/02_Track_Payments.py", label="Track Payments", icon="💸")

def expense_history_nav():
    st.sidebar.page_link("pages/03_Expense_History.py", label="Expense History", icon="📋")

# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # Logo appears at the top of the sidebar on every page
    st.sidebar.image("assets/logo.png", width=150)

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        home_nav()

    if st.session_state["authenticated"]:

         if st.session_state["role"] == "jude":
            jude_home_nav()
            add_expense_nav()
            track_payments_nav()
            expense_history_nav()

    # About link appears at the bottom for all roles
    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
