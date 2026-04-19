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

# ---- Role: daniel -----------------------------------------------------------

def daniel_home_nav():
    st.sidebar.page_link("pages/10_Daniel_Home.py", label="Daniel's Home", icon="🏠")

def log_club_expense_nav():
    st.sidebar.page_link("pages/11_Log_Club_Expense.py", label="Log Club Expense", icon="➕")

def reimbursements_nav():
    st.sidebar.page_link("pages/12_Reimbursements.py", label="Reimbursements", icon="💸")

def budget_summary_nav():
    st.sidebar.page_link("pages/13_Budget_Summary.py", label="Budget Summary", icon="📊")

# ---- Role: sofia ------------------------------------------------------------

def sofia_home_nav():
    st.sidebar.page_link("pages/20_Sofia_Home.py", label="Sofia's Home", icon="🏠")

def manage_categories_nav():
    st.sidebar.page_link("pages/21_Manage_Categories.py", label="Manage Categories", icon="🗂️")

def flagged_transactions_nav():
    st.sidebar.page_link("pages/22_Flagged_Transactions.py", label="Flagged Transactions", icon="🚩")

def support_issues_nav():
    st.sidebar.page_link("pages/23_Support_Issues.py", label="Support Issues", icon="🛠️")

# ---- Role: rachel -----------------------------------------------------------

def rachel_home_nav():
    st.sidebar.page_link("pages/30_Rachel_Home.py", label="Rachel's Home", icon="🏠")

def spending_by_category_nav():
    st.sidebar.page_link("pages/31_Spending_By_Category.py", label="Spending by Category", icon="📈")

def student_group_nav():
    st.sidebar.page_link("pages/32_Student_Group_Analysis.py", label="Student Group Analysis", icon="👥")

def dashboard_filters_nav():
    st.sidebar.page_link("pages/33_Dashboard_Filters.py", label="Dashboard Filters", icon="🔍")

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

        if st.session_state["role"] == "daniel":
            daniel_home_nav()
            log_club_expense_nav()
            reimbursements_nav()
            budget_summary_nav()

        if st.session_state["role"] == "sofia":
            sofia_home_nav()
            manage_categories_nav()
            flagged_transactions_nav()
            support_issues_nav()

        if st.session_state["role"] == "rachel":
            rachel_home_nav()
            spending_by_category_nav()
            student_group_nav()
            dashboard_filters_nav()

    # About link appears at the bottom for all roles
    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
