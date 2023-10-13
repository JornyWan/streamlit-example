import streamlit as st
# from io import StringIO
# import os
from decouple import config
import json
import re     # for email address validation
import tensorflow as tf
import numpy as np
import streamlit_authenticator as stauth
from streamlit_modal import Modal   # Used for creating popout modal
from streamlit_cookies_manager import EncryptedCookieManager  # Using cookie to store session data

from datetime import datetime, timedelta
import mongoAuthHelper



# """
# # Stress Intensity Factor Calculator (Proof of Concept)

# """


# Global variables, settings and initializations
model = None
record_num = 0
SESSION_VALID_LENGTH = 7    # 7 days
CRED_ENV_FILE_NAME = "cred.json"
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




# # Test the function
# result = mongoAuthHelper.update_document_by_email(
#     "example@email.com", "Updated Name2222", "updated_password", ["updated_model1", "updated_model2"]
# )
# print(f"Number of documents updated: {updated_count}")

# # Test the function
# result = mongoAuthHelper.insert_document("example@email.com", "Example NameSS", "example_password", ["model1", "model2"])
# print(f"Inserted document with ID: {inserted_id}")


# Test the function
# result = mongoAuthHelper.fetch_document_by_email("dev@iowt-now.com")
# st.write(result['document'])





def load_model(a,b,w,l0,l1,p):
    global model
    model = tf.keras.models.load_model('models/NN_4_64_64_1/converted_model.h5')
    a = np.array([[1, 1, 1, 1]])
    pred = model.predict(a)
    st.write('a shape:', a.shape)
    st.write('pred:', pred)



def KP(a, b, w, l0, l1):
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


def display_values(a, b, w, l0, l1, P, K_o, record_num):
    print(type(a), type(b), type(w), type(l0), type(l1), type(P), type(K_o))
    try:
        K_o = float(K_o)
        str_output = ("a={:.3f}, b={:.3f}, w={:.3f}, L0={:.3f}, L1={:.3f}, P={:.3f}, KI={:.3f}".format(a, b, w, l0, l1, P, K_o))
        
        
        st.write(str_output)
        st.write('Empirical:  {:.3f}'.format(emp2(a, b, w, l1, P)))
        
        if (0.1 <= a/b <= 0.8 and 1.0 <= w/b <= 3.0 and
            0.1 <= l0/b <= 0.4 and 2.0 <= l1/b <= 5.0):
            st.markdown(':smile: Interpolation')
            st.write("Record {}:  {} (Interpolation)".format(pad(record_num, 3), str_output))
        else:
            st.markdown(':frowning_face: Extrapolation')
            st.write("Record {}:  {} (Extrapolation)".format(pad(record_num, 3), str_output))
        
        st.write("KI Value: {:.3f}".format(K_o))
    except:
        st.write("invalid input!")




def emp2(a, b, w, L, P):
    F = 1.85 - 3.38*(a/b) + 13.24*pow(a/b, 2) - 23.26*pow(a/b, 3) + 16.8*pow(a/b, 4)
    y = (pow(b, 2) * w / 2 + pow(w, 2) / 4 * (b + w / 6)) / (b * w + pow(w, 2) / 4)
    I = (w*pow(b, 3)/12 + pow(y-b/2, 2)*b*w + pow(w, 4)/288 + pow(w/6+b-y, 2)*pow(w, 2)/4)
    sigma = P * L * y / I
    return sigma * (pow(a, 0.5) * 3.14159) * F


def pad(n, width, z='0'):
    return (str(z) * (width - len(str(n))) + str(n))


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

def getCredByUsername(username):
    data = json.load(open(CRED_ENV_FILE_NAME))
    creds = data['credentials']['registered_users']

    if creds:
        for cred in creds:
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


def renderAuthModals(isLoggedIn, cookies):
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
                        loginResult = verifyUser(username, password)

                        if loginResult['success']:
                            writeLoggedInUserToCookie(cookies, username)
                            st.success(loginResult['message'])
                        else:
                            st.error(loginResult['message'])

        else: 
            runLogout = st.button("Logout")
            if runLogout:
                LOGGED_IN_USER_NAME = ''
                cookies['logged_in_user_username'] = ''
                cookies['logged_in_users_name'] = ''
                cookies['session_expire_on'] = ''
                cookies.save()
                st.rerun()
            


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
        # To read file as string:
        data = json.load(uploaded_file)
        st.write(data)


        # TODO: Check parsing json and apply model equation


sessionData = getLoggedInUserFromCookie(cookies)
print(sessionData)

if LOGGED_IN_USER_NAME:
    st.title("Hi " + LOGGED_IN_USER_NAME + "!")
else:
    st.title("Please log in!")

renderAuthModals(sessionData['success'], cookies)


col1, col2 = st.columns(2, gap="medium")
with col1:
   st.image("./public/Notched_cantilever_sketch.png")

with col2:
   with st.container():
    st.components.v1.iframe(iframe_src_3d_url, scrolling=False)

# load demo model here
# load_model()

model = tf.keras.models.load_model('models/NN_4_64_64_1/converted_model.h5')
if b == 0:
   st.write('Please input parameters!')
else:
    kop = KP(a,b,w,LZero,LOne)
    ki = kop * P
    st.write('KI:', ki)

    display_values(a, b, w, LZero, LOne, P, ki, record_num)

st.write("*****DEBUG: Current cookies:", cookies)


# st.components.v1.iframe(iframe_src_3d_url, width=800, height = 600, scrolling=False)

