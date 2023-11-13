import streamlit as st

def runUiSetUp(showLogo):
    if showLogo:
        st.image("./public/web_title.png")

    # remove the weird blank forehead from the content block on the web page
    # hacky way due to current streamlit limiations as of Oct 2023
    st.markdown("""
    <style>
        #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    </style>

    """, unsafe_allow_html=True)


def loadSourceCodeWidget():
    PIS_SOURCE_CODE = "<h3>Pillar Indentation Splitting: <a href=\"https://github.com/hint1412/XLiu.github.io/tree/master/SIF/\">Source Code</a></h3>"
    st.markdown(PIS_SOURCE_CODE, unsafe_allow_html=True)

    PPCC_SOURCE_CODE = "<h3>Pre-notched Pentagonal Cross-section Cantilevers: <a href=\"https://github.com/hint1412/XLiu.github.io/tree/master/SIF/\">Source Code</a></h3>" 
    st.markdown(PPCC_SOURCE_CODE, unsafe_allow_html=True)


def updateResult(modelResult):
    resultsTxtAreaKey = 'resultsTxtArea'
    
    if resultsTxtAreaKey not in st.session_state:
        st.session_state[resultsTxtAreaKey] = "Please provide your inputs"
                
    if not modelResult["success"]:
        return

    st.session_state[resultsTxtAreaKey] = "Inputs: \n" + modelResult["str_output"] + "\n\nOutputs:\n" + "KI: " + modelResult["ki_value"] + "\n" + modelResult["type"]

    st.text_area("Results:", value=st.session_state[resultsTxtAreaKey], key=resultsTxtAreaKey, height=200, disabled=True)
