import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager  # Using cookie to store session data
from decouple import config

import mongoAuthenticator
import authHelper
import uiHelper


cookies = EncryptedCookieManager(
    # This prefix will get added to all your cookie names.
    # So that the app can avoid cookie name clashes with other apps on Streamlit Cloud
    prefix = "stress-ai-",
    # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
    password = config('COOKIES_PASSWORD')
)

if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()

LOGGED_IN_USER_NAME = cookies.get('logged_in_users_name')

def renderAuthModals(isLoggedIn, cookies):
    # render login/logout/createAccount buttons
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if isLoggedIn:
            st.success("Successfully logged in!")
            runLogout = st.button("Logout")
            
            if runLogout:
                LOGGED_IN_USER_NAME = ''
                cookies['logged_in_user_username'] = ''
                cookies['logged_in_users_name'] = ''
                cookies['session_expire_on'] = ''
                cookies.save()
                st.rerun()

        else:
            login_username = st.text_input("Login Username (email)", key="login_username")
            login_password = st.text_input("Login Password", type="password")

            if st.button("Login"):
                loginResult = authHelper.verifyUser(login_username, login_password)
                print("loginResult", loginResult)

                if loginResult['success']:
                    authHelper.writeLoggedInUserToCookie(cookies, login_username)

                    # success message will not show due to streamlit re-rendering flow - should be ok
                    st.success(loginResult['message'])
                else:
                    st.error(loginResult['message'])


    with col2:
        new_username = st.text_input("Username (Please use your email address)", key="new_username")
        user_full_name = st.text_input("Your Name", key="name")
        new_password = st.text_input("Password", type="password")
        retyped_password = st.text_input("Please Retype Password", type="password")

        if st.button("Create account"):
            if not authHelper.validateInput(new_username, "email", 5):
                st.error("Error: " + new_username + " is not a valid email address!")
                return
            
            if not authHelper.validateInput(user_full_name, '', 5):
                st.error("Error: name must be longer than 5 characters!")
                return

            if not authHelper.validateInput(new_password, '', 8):
                st.error("Error: password must be longer than 8 characters!")   
                return 

            if not retyped_password == new_password:
                st.error("Error: " + new_username + " re-typed password must match password provided!")
                return

            result = mongoAuthenticator.insert_document(str(new_username), str(user_full_name), str(new_password), [])
            if result["success"]:
                st.success(result["message"])
            else:
                st.error(result["message"])
    

uiHelper.runUiSetUp(False)

sessionData = authHelper.getLoggedInUserFromCookie(cookies)

# st.write("*****DEBUG: Current cookies:")
# st.write(sessionData)

st.header('Authentication', divider='rainbow')

if LOGGED_IN_USER_NAME:
    st.header("Hi " + LOGGED_IN_USER_NAME + "!")
else:
    st.header("Please log in or register!")

renderAuthModals(sessionData['success'], cookies)