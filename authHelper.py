import streamlit as st
# from io import StringIO
# import os
from decouple import config
import re     # for email address validation
import tensorflow as tf
import numpy as np
import streamlit_authenticator as stauth
from streamlit_modal import Modal   # Used for creating popout modal
from streamlit_cookies_manager import EncryptedCookieManager  # Using cookie to store session data

from datetime import datetime, timedelta
import mongoAuthenticator


SESSION_VALID_LENGTH = 7    # 7 days


# Login page
def getCredByUsername(username):
    data = mongoAuthenticator.fetch_document_by_email(username)
    if 'document' not in data:
        return {
            "success": False,
        }
    
    cred = data['document']

    if cred['email'] == username:
        return {
            "success": True,
            "credObj": cred
        }

    return {
        "success": False,
    }


# Load user data from the JSON file
# Verify user credentials
def verifyUser(username, password):
    response = getCredByUsername(username)

    if not response['success']:
        return {
            "success": False,
            "message": "Failed to login. Could not find an account with provided username. Please create an account!"
        }
    
    if response['credObj']['password'] == password:
        return {
            "success": True,
            "message": "Logged in successfully!"
        }
    
    return {
        "success": False,
        "message": "Failed to login. Incorrect Password"
    }



def isValidEmail(email):
    # This is a common and simple regex pattern for email validation. It checks for:
    # 1. One or more alphanumeric characters (or .-_ characters).
    # 2. Followed by an '@' symbol.
    # 3. Followed again by one or more alphanumeric characters (or .-_ characters).
    # 4. A period (.)
    # 5. And finally, 2 to 6 alphanumeric characters. (To match common TLDs like .com, .org, .co.uk, etc.)
    pattern = r"^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$"
    
    if re.match(pattern, email):
        return True
    return False


def validateInput(input, type, minLength):
    if len(input) < minLength:
        return False

    if type == "email": 
        return isValidEmail(input)
    
    return True


def writeLoggedInUserToCookie(cookies, username):
    # Save the value to cookie, this will get saved on next rerun automatically
    credResponse = getCredByUsername(username)
    LOGGED_IN_USER_NAME = credResponse['credObj']['name'] if credResponse['success'] else ''

    cookies['logged_in_user_username'] = username
    cookies['logged_in_users_name'] = LOGGED_IN_USER_NAME
    cookies['session_expire_on'] = str(datetime.today() + timedelta(days = SESSION_VALID_LENGTH))
    
    # saving the cookies now, without a rerun
    # cookies.save()
    st.rerun()


def getLoggedInUserFromCookie(cookies):
    # Save the value to cookie, this will get saved on next rerun automatically
    
    try:
        username = cookies.get('logged_in_user_username')
        name = cookies.get('logged_in_users_name')
        session_expire_on = cookies.get('session_expire_on')

        if username and session_expire_on:
            sessionEndTime = datetime.strptime('2023-11-02 17:24:33.008281', '%Y-%m-%d %H:%M:%S.%f')

            if sessionEndTime > datetime.now():
                return {
                    'success': True,
                    'username': username,
                    'name': name
                }
            
    except:
        print("No cookies found!")
    
    return {
        'success': False
    }