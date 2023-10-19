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