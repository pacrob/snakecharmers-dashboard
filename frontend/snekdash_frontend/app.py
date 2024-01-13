import requests
import streamlit as st

st.title("Data Viewer")


def fetch_root_data():
    """Fetch data from the backend and returns it as a JSON object."""
    try:
        response = requests.get("http://backend:8000/")
        print(response)
        return response.json()
    except requests.RequestException as e:
        return str(e)


# Displaying data
if st.button("Fetch Root Data"):
    data = fetch_root_data()
    if data:
        st.json(data)
    else:
        st.error("Failed to fetch root data.")


def fetch_newsfragment_data():
    """Fetch data from the backend and returns it as a JSON object."""
    try:
        response = requests.get("http://backend:8000/newsfragments")
        print(response)
        # return json.dumps({"response": response})
        return response.json()
    except requests.RequestException as e:
        return str(e)


# Displaying data
if st.button("Fetch Newsfragment Data"):
    data = fetch_newsfragment_data()
    if data:
        st.json(data)
    else:
        st.error("Failed to fetch newsfragment data.")

# To run the frontend, use: streamlit run app.py
