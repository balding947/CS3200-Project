import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Manage Dashboard Filters")
st.write("View, add, update, and remove dashboard filters.")

try:
    response = requests.get(f"{API_URL}/dashboard-filters?user_id=4")
    filters = response.json()
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
    filters = []

st.subheader("Your Active Filters")
active = [f for f in filters if f["is_active"]]
inactive = [f for f in filters if not f["is_active"]]

if not active:
    st.info("No active filters.")
else:
    for f in active:
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.write(f"**{f['filter_type']}:** {f.get('value', 'N/A')}")
        with col2:
            st.write(":green[active]")
        with col3:
            if st.button("Deactivate", key=f"deact_{f['filter_id']}"):
                try:
                    r = requests.put(
                        f"{API_URL}/dashboard-filters/update/{f['filter_id']}",
                        json={"is_active": 0}
                    )
                    if r.status_code == 200:
                        st.success("Filter deactivated!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

st.subheader("Inactive Filters")
if not inactive:
    st.info("No inactive filters.")
else:
    for f in inactive:
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            st.write(f"**{f['filter_type']}:** {f.get('value', 'N/A')}")
        with col2:
            st.write(":red[inactive]")
        with col3:
            if st.button("Reactivate", key=f"react_{f['filter_id']}"):
                try:
                    r = requests.put(
                        f"{API_URL}/dashboard-filters/update/{f['filter_id']}",
                        json={"is_active": 1}
                    )
                    if r.status_code == 200:
                        st.success("Filter reactivated!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        with col4:
            if st.button("Delete", key=f"del_{f['filter_id']}"):
                try:
                    r = requests.delete(
                        f"{API_URL}/dashboard-filters/delete/{f['filter_id']}"
                    )
                    if r.status_code == 200:
                        st.success("Filter deleted!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

st.divider()
st.subheader("Add a New Filter")

with st.form("add_filter_form"):
    filter_type = st.selectbox("Filter Type", [
        "date_range", "semester", "category",
        "housing_type", "club_budget", "status", "view_mode"
    ])
    filter_value = st.text_input("Value (e.g. 'Fall 2025', 'active')")
    is_active = st.radio("Active?", ["Yes", "No"])
    submitted = st.form_submit_button("Add Filter", type="primary")

    if submitted:
        if not filter_value:
            st.error("Please enter a filter value.")
        else:
            next_id = max([f["filter_id"] for f in filters], default=0) + 1
            payload = {
                "filter_id": next_id,
                "filter_type": filter_type,
                "value": filter_value,
                "is_active": 1 if is_active == "Yes" else 0,
                "user_id": 4
            }
            try:
                r = requests.post(f"{API_URL}/dashboard-filters", json=payload)
                if r.status_code == 201:
                    st.success("Filter added!")
                    st.rerun()
                else:
                    st.error(f"Error: {r.json().get('error')}")
            except Exception as e:
                st.error(f"Could not connect to the API: {e}")

if st.button("Back to Home"):
    st.switch_page("pages/30_Rachel_Home.py")