import streamlit as st
import psycopg2

st.title("Connection Test")

try:
    conn = psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        port=st.secrets["postgres"]["port"],
        dbname=st.secrets["postgres"]["dbname"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
    )
    st.success("Connected successfully!")
    conn.close()
except Exception as e:
    st.error(f"Connection failed: {e}")