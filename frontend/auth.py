import streamlit as st
import requests
import os

API_URL = "http://127.0.0.1:8000"  # FastAPI backend

# ---------------- SIGN UP ---------------- #
def signup_page():
    st.title("Create Account")

    full_name = st.text_input("Full Name")
    username = st.text_input("Username (unique)")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if not full_name or not username or not password:
            st.warning("Please fill all fields.")
            return
        if password != confirm:
            st.error("Passwords do not match.")
            return

        try:
            res = requests.post(f"{API_URL}/signup", json={
                "name": full_name,
                "username": username,
                "password": password
            })
            if res.status_code == 200:
                data = res.json()
                st.success("Account created successfully! Please log in.")
                st.balloons()
            elif res.status_code == 400:
                st.error("Username already exists. Try another one.")
            else:
                st.error(f"Unexpected error: {res.status_code} — {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to backend API. Make sure FastAPI is running.")


# ---------------- LOGIN ---------------- #
def login_page():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.warning("Please enter both username and password.")
            return

        try:
            res = requests.post(f"{API_URL}/login", json={
                "username": username,
                "password": password
            })

            if res.status_code == 200:
                data = res.json()
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = data["user_id"]
                st.session_state["username"] = data["username"]
                st.session_state["name"] = data["name"]
                st.session_state["genre"] = data.get("preferred_genre", "")
                st.success(f"Welcome back, {data['username']} 👋")
                st.rerun()
            else:
                st.error("Invalid username or password.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to backend API. Make sure FastAPI is running.")