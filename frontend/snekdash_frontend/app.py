import requests
import streamlit as st

st.title("Data Viewer")


def fetch_data_from_backend():
    """Fetch data from the backend and returns it as a JSON object."""
    try:
        response = requests.get("http://backend:5000/data")
        return response.json()
    except requests.RequestException as e:
        return str(e)


# Displaying data
if st.button("Fetch Data"):
    data = fetch_data_from_backend()
    if data:
        st.json(data)
    else:
        st.error("Failed to fetch data.")

# To run the frontend, use: streamlit run app.py
