from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
from io import StringIO
# import tensorflow as tf
import numpy as np
import streamlit_authenticator as stauth
from streamlit_modal import Modal
import json
import re     # for email address validation
 


# """
# # Stress Intensity Factor Calculator (Proof of Concept)

# """


# Global variables and settings
model = None
record_num = 0
iframe_src_3d_url = "https://3dwarehouse.sketchup.com/embed/9658ccab-6ac3-4b89-a23f-635206942357"
CRED_ENV_FILE_NAME = "cred.json"

st.set_page_config("Stress Intensity Factor Calculator", layout="wide")


def load_model():
    global model
    model = tf.keras.models.load_model('models/NN_4_64_64_1/converted_model.h5')
    a = np.array([[1, 1, 1, 1]])
    pred = model.predict(a)
    st.write('a shape:', a.shape)
    st.write('pred:', pred)


def KP(a, b, w, l0, l1, P):
    inputs = np.array([[a / b, w / b, l0 / b, l1 / b]])
    outputs = model.predict(inputs)
    kop = (outputs * l1 * (a ** 0.5) / b / w / w)
    return kop if np.isfinite(kop) else 0.0


def emp(a, b, w, L, P):
    F = 1.85 - 3.38 * (a / b) + 13.24 * (a / b) ** 2 - 23.26 * (a / b) ** 3 + 16.8 * (a / b) ** 4
    y = (b * b * w / 2 + w * w / 4 * (b + w / 6)) / (b * w + w * w / 4)
    I = w * b ** 3 / 12 + (y - b / 2) ** 2 * b * w + w ** 4 / 288 + (w / 6 + b - y) ** 2 * w * w / 4
    sigma = P * L * y / I
    return sigma * np.sqrt(np.pi * a) * F

def runUiSetUp():
    st.image("./public/web_title.png")
    st.markdown("""
    <style>
            .block-container {
                margin-top: -2rem;
                
            }    
    </style>
    """, unsafe_allow_html=True)



# Login page
# Load user data from the JSON file
# Verify user credentials
def verify_user(username, password):
    data = json.load(open(CRED_ENV_FILE_NAME))
    creds = data['credentials']['registered_users']

    if creds:
        for cred in creds:
            if cred['email'] == username:
                if cred['password'] == password:
                     return {
                        "success": True,
                        "message": "Logged in successfully!"
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to login. Incorrect Password"
                    }
                
    return {
        "success": False,
        "message": "Failed to login. Could not find an account with provided username. Please create an account!"
    }


def createUserAccount(email, name, password):
    data = json.load(open(CRED_ENV_FILE_NAME))

    data['credentials']['registered_users'].append({
        'email': str(email), 
        'name': str(name), 
        'password': str(password), 
        'models': []
    })

    print("after addition, data is ", data)

    try:
        with open(CRED_ENV_FILE_NAME, "w") as f:
            f.write(json.dumps(data))
            return True
    except:
        print("Error during writing to data.json")

    return False


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


def renderLogin(isLoggedIn):
    # render login/logout/createAccount buttons
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        if not isLoggedIn:
            loginModal = Modal("Authentication", key="loginModal", max_width=700)
            runLogin = st.button("Login")

            # scripts for login modal
            if(runLogin):
                loginModal.open()

            if loginModal.is_open():
                with loginModal.container():
                    username = st.text_input("Username", key="username")
                    password = st.text_input("Password", type="password")

                    if st.button("Submit"):
                        loginResult = verify_user(username, password)

                        if loginResult['success']:
                            st.success(loginResult['message'])
                        else:
                            st.error(loginResult['message'])

        else: 
            runLogout = st.button("Logout")
            

    with col2:
        accountCreationModal = Modal("Create an account", key="accountCreationModal", max_width=700)
        createAccount = st.button("Create an account")

        if(createAccount):
            accountCreationModal.open()

        if accountCreationModal.is_open():
            with accountCreationModal.container():
                username = st.text_input("Username (Please use your email address)", key="username")
                name = st.text_input("Name", key="name")
                password = st.text_input("Password", type="password")
                passwordRetype = st.text_input("Retype Password", type="password")

                if st.button("Create account"):
                    if not validateInput(username, "email", 5):
                        st.error("Error: " + username + " is not a valid email address!")
                        return
                    
                    if not validateInput(name, '', 5):
                        st.error("Error: name must be longer than 5 characters!")
                        return

                    if not validateInput(password, '', 8):
                        st.error("Error: password must be longer than 8 characters!")   
                        return 

                    if not passwordRetype == password:
                        st.error("Error: " + username + " re-typed password must match password provided!")
                        return

                    if createUserAccount(username, name, password):
                        st.success("Successfully created account for " + name + "! Your username is: " + username)



# add sideBar
with st.sidebar:
    runUiSetUp()

    a = st.number_input("a (μm)", help="a; unit: μm", key="a")
    b = st.number_input("b (μm)", help="b; unit: μm", key="b")
    w = st.number_input("w (μm)", help="w; unit: μm", key="w")
    LZero = st.number_input("L0 (μm)", help="L0; unit: μm", key="l_zero")
    LOne = st.number_input("L1 (μm)", help="L1; unit: μm", key="l_one")
    P = st.number_input("P (mN)", help="P; unit: mN", key="p")

    uploaded_file = st.file_uploader("Upload your model here", key="user_custom_model", type = "json")
    if uploaded_file is not None:
        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        st.write(stringio)

        # To read file as string:
        string_data = stringio.read()
        st.write(string_data)

        # Can be used wherever a "file-like" object is accepted:
        dataframe = pd.read_json(uploaded_file)
        st.write(dataframe.to_json())


        # TODO: Check parsing json and apply model equation

# load demo model here
# load_model()


renderLogin(False)

st.write("(PoC) Assuming model equation is: a + b + w + LZero + LOne + P. Result is: " )
st.write(str(a + b + w + LZero + LOne + P))

col1, col2 = st.columns(2, gap="medium")
with col1:
   st.image("https://hint1412.github.io/XLiu.github.io/SIF/images/Notched_cantilever_sketch.png")

with col2:
   with st.container():
    st.components.v1.iframe(iframe_src_3d_url, scrolling=False)

    


# st.components.v1.iframe(iframe_src_3d_url, width=800, height = 600, scrolling=False)
# st.components.v1.html(image_html_block, width=800, height=600, scrolling=False)

