import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Manage Categories")
st.write("Add new categories or update existing ones.")

try:
    response = requests.get(f"{API_URL}/categories")
    categories = response.json()
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
    categories = []

st.subheader("Existing Categories")
for cat in categories:
    col1, col2, col3 = st.columns([4, 2, 2])
    with col1:
        st.write(f"**{cat['name']}**")
    with col2:
        status_color = "green" if cat["status"] == "active" else "red"
        st.write(f":{status_color}[{cat['status']}]")
    with col3:
        if cat["status"] == "active":
            if st.button("Mark Inactive", key=f"deact_{cat['category_id']}"):
                try:
                    r = requests.put(
                        f"{API_URL}/categories/update/{cat['category_id']}",
                        json={"status": "inactive"}
                    )
                    if r.status_code == 200:
                        st.success(f"{cat['name']} marked inactive!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            if st.button("Mark Active", key=f"act_{cat['category_id']}"):
                try:
                    r = requests.put(
                        f"{API_URL}/categories/update/{cat['category_id']}",
                        json={"status": "active"}
                    )
                    if r.status_code == 200:
                        st.success(f"{cat['name']} marked active!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

st.divider()
st.subheader("Add a New Category")

with st.form("add_category_form"):
    new_name = st.text_input("Category Name")
    new_status = st.radio("Status", ["active", "inactive"])
    submitted = st.form_submit_button("Save Category", type="primary")
    if submitted:
        if not new_name:
            st.error("Please enter a category name.")
        else:
            next_id = max([c["category_id"] for c in categories], default=0) + 1
            payload = {
                "category_id": next_id,
                "name": new_name,
                "status": new_status
            }
            try:
                r = requests.post(f"{API_URL}/categories", json=payload)
                if r.status_code == 201:
                    st.success(f"Category '{new_name}' added!")
                    st.rerun()
                else:
                    st.error(f"Error: {r.json().get('error')}")
            except Exception as e:
                st.error(f"Could not connect to the API: {e}")

if st.button("Back to Home"):
    st.switch_page("pages/20_Sofia_Home.py")
