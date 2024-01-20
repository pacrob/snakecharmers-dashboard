import requests
import streamlit as st

ROOT_BACKEND_URL = "http://backend:8000/"

st.title("Data Viewer")


def lprint(to_print: str):
    """Print out to docker compose log in the terminal."""
    print(to_print, flush=True)


def fetch_root_data():
    """Fetch data from the backend and returns it as a JSON object."""
    try:
        response = requests.get(ROOT_BACKEND_URL)
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
        response = requests.get(f"{ROOT_BACKEND_URL}newsfragments")
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


def fetch_db_data():
    """Fetch data from the backend and returns it as a JSON object."""
    try:
        response = requests.get(f"{ROOT_BACKEND_URL}data")
        print(response)
        # return json.dumps({"response": response})
        return response.json()
    except requests.RequestException as e:
        return str(e)


# Displaying data
if st.button("Fetch Database Data"):
    data = fetch_db_data()
    if data:
        st.json(data)
    else:
        st.error("Failed to fetch newsfragment data.")


def post_data_to_backend(input_text):
    """Post data to the backend."""
    try:
        response = requests.post(f"{ROOT_BACKEND_URL}data", data={"data": input_text})
        return response.json()
    except requests.RequestException as e:
        return str(e)


# input_text = st.text_input("Enter text")
if st.button("Submit"):
    lprint("Button clicked")
    response = post_data_to_backend("cats")
    lprint(f"{response=}")
    if response:
        st.json(response)
    else:
        st.error("Failed to post the data to the backend.")
# To run the frontend, use: streamlit run app.py
