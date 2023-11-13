import streamlit as st
from decouple import config
import json
import tensorflow as tf
import numpy as np
import streamlit_authenticator as stauth
from streamlit_modal import Modal   # Used for creating popout modal
from streamlit_cookies_manager import EncryptedCookieManager  # Using cookie to store session data

import authHelper
import uiHelper
import modelSimulator
import modelManager


# """
# # Stress Intensity Factor Calculator (Proof of Concept)

# """

# Global variables, settings and initializations
record_num = 0
iframe_src_3d_url = "https://3dwarehouse.sketchup.com/embed/9658ccab-6ac3-4b89-a23f-635206942357"
st.set_page_config("Stress Intensity Factor Calculator", layout="wide")

# This should be on top of your script
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

sessionData = authHelper.getLoggedInUserFromCookie(cookies)
print(sessionData)


# add sideBar
with st.sidebar:
    uiHelper.runUiSetUp(True)

    a = st.number_input("a (μm)", help="a; unit: μm", key="a")
    b = st.number_input("b (μm)", help="b; unit: μm", key="b")
    w = st.number_input("w (μm)", help="w; unit: μm", key="w")
    LZero = st.number_input("L0 (μm)", help="L0; unit: μm", key="l_zero")
    LOne = st.number_input("L1 (μm)", help="L1; unit: μm", key="l_one")
    P = st.number_input("P (mN)", help="P; unit: mN", key="p")
    
    # hashedUserName = "NN_4_16_8_1_test"

    if LOGGED_IN_USER_NAME: 
        hashedUserName = authHelper.hashStringMd5(LOGGED_IN_USER_NAME)

        options = ["Default"]
        options.extend(modelManager.getAvailableModels(hashedUserName))
        options.append("Upload New")

        # Create the choice list with a select box
        selected_option = st.selectbox("Choose an option:", options)
        # Do something with the selected option
        st.write(f"You selected: {selected_option}")

        if selected_option == "Upload New":
            uploaded_file = st.file_uploader("Upload your model here", key="user_custom_model", type = "h5")
            if uploaded_file is not None:
                modelManager.storeUserModel(hashedUserName, "test data", uploaded_file.name)
                st.success("Sucessfully uploaded model: " + uploaded_file.name + "! You can now test it in our web app!")


if LOGGED_IN_USER_NAME:
    st.header("Hi " + LOGGED_IN_USER_NAME + "!", divider='rainbow')
else:
    st.header("Hi guest! Please consider logging in!", divider='rainbow')

uiHelper.loadSourceCodeWidget()

col1, col2 = st.columns(2, gap="medium")
with col1:
    st.image("./public/Notched_cantilever_sketch.png")

with col2:
    with st.container():
        st.components.v1.iframe(iframe_src_3d_url, scrolling=False)


# load pre-defined default model here
st.header("Model Simulation", divider='rainbow')
model = tf.keras.models.load_model('./models/NN_4_64_64_1/converted_model.h5')

modelResult = {"success": False}

if b == 0:
   st.text_area("Results:", value="Please input parameters!", height=200, disabled=True)
else:
    ki = modelSimulator.KP(model,a,b,w,LZero,LOne) * P
    modelResult = modelSimulator.getDisplayValues(a, b, w, LZero, LOne, P, ki, record_num)
    
    uiHelper.updateResult(modelResult)



# st.components.v1.iframe(iframe_src_3d_url, width=800, height = 600, scrolling=False)

