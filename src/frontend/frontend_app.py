import streamlit as st
import requests
import json

st.title('Data Viewer')

# Function to fetch data from the backend
def fetch_data_from_backend():
    try:
        response = requests.get("http://backend:5000/data")
        return response.json()
    except requests.RequestException as e:
        return str(e)

# Displaying data
if st.button('Fetch Data'):
    data = fetch_data_from_backend()
    if data:
        st.json(data)
    else:
        st.error("Failed to fetch data.")

# To run the frontend, use: streamlit run frontend_app.py
