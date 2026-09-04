import streamlit as st 
import requests



if st.button("Get Insights"):
    response=requests.get("http://127.0.0.1:8000/ping")
    data=response.json()
    st.write(data["explanation"])