import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_URL = "http://web-api:4000"

st.title("Support Issues")
st.write("View and manage app support issues.")

try:
    response = requests.get(f"{API_URL}/analytics/support-issues")
    if response.status_code == 200:
        all_issues = response.json()
    else:
        st.error("Could not load support issues.")
        all_issues = []
except Exception as e:
    st.error(f"Could not connect to the API: {e}")
    all_issues = []

open_issues = [i for i in all_issues if i["status"] == "open"]
in_progress = [i for i in all_issues if i["status"] == "in_progress"]
resolved = [i for i in all_issues if i["status"] == "resolved"]
closed = [i for i in all_issues if i["status"] == "closed"]

st.subheader("Issue Summary")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Open", len(open_issues))
with col2:
    st.metric("In Progress", len(in_progress))
with col3:
    st.metric("Resolved", len(resolved))
with col4:
    st.metric("Closed", len(closed))

st.divider()

status_filter = st.selectbox(
    "Filter by Status",
    ["open", "in_progress", "resolved", "closed", "all"]
)

if status_filter == "all":
    filtered = all_issues
else:
    filtered = [i for i in all_issues if i["status"] == status_filter]

st.write(f"Showing {len(filtered)} issues")

for issue in filtered:
    description_preview = issue["description"][:60] if issue.get("description") else "No description"

    with st.expander(f"Issue #{issue['issue_id']} — {description_preview}"):
        st.write(f"**Status:** {issue['status']}")
        st.write(f"**Submitted by:** {issue.get('submitted_by', 'N/A')}")
        st.write(f"**Created at:** {issue.get('created_at', 'N/A')}")

        col1, col2 = st.columns(2)

        with col1:
            if issue["status"] == "open":
                if st.button("Mark In Progress", key=f"prog_{issue['issue_id']}"):
                    try:
                        update = requests.put(
                            f"{API_URL}/support-issues/update/{issue['issue_id']}",
                            json={"status": "in_progress"}
                        )

                        if update.status_code == 200:
                            st.success("Status updated to In Progress!")
                            st.rerun()
                        else:
                            try:
                                error_message = update.json().get("error", "Unknown error")
                            except Exception:
                                error_message = "Unknown error"
                            st.error(f"Could not update issue: {error_message}")
                    except Exception as e:
                        st.error(f"Could not connect to the API: {e}")

        with col2:
            if issue["status"] in ["open", "in_progress"]:
                if st.button("Mark Resolved", key=f"res_{issue['issue_id']}"):
                    try:
                        update = requests.put(
                            f"{API_URL}/support-issues/update/{issue['issue_id']}",
                            json={"status": "resolved"}
                        )

                        if update.status_code == 200:
                            st.success("Status updated to Resolved!")
                            st.rerun()
                        else:
                            try:
                                error_message = update.json().get("error", "Unknown error")
                            except Exception:
                                error_message = "Unknown error"
                            st.error(f"Could not update issue: {error_message}")
                    except Exception as e:
                        st.error(f"Could not connect to the API: {e}")

if st.button("Back to Home"):
    st.switch_page("pages/20_Sofia_Home.py")