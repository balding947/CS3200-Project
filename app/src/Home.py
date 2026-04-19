##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

# streamlit supports regular and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout='wide')

# If a user is at this page, we assume they are not
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false.
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel.
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

logger.info("Loading the Home page of the app")
st.title('Orbit')
st.write('#### Hi! As which user would you like to log in?')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.

if st.button('Act as Jude Bellingham, a Student Roommate',
             type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'jude'
    st.session_state['first_name'] = 'Jude'
    st.session_state['user_id'] = 7
    st.switch_page('pages/00_Jude_Home.py')

if st.button('Act as Daniel Kim, a Club Budget Manager',
             type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'daniel'
    st.session_state['first_name'] = 'Daniel'
    st.session_state['user_id'] = 11
    st.switch_page('pages/10_Daniel_Home.py')

if st.button('Act as Sofia Patel, a Support Coordinator',
             type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'sofia'
    st.session_state['first_name'] = 'Sofia'
    st.session_state['user_id'] = 3
    st.switch_page('pages/20_Sofia_Home.py')

if st.button('Act as Rachel Nguyen, a Financial Wellness Coordinator',
             type='primary', use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'rachel'
    st.session_state['first_name'] = 'Rachel'
    st.session_state['user_id'] = 4
    st.switch_page('pages/30_Rachel_Home.py')
