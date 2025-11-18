import streamlit as st
import pandas as pd

# DB 연결
@st.cache_resource
def get_db_connection():
    try:
        conn = st.connection("supabase_db", type="sql")
        return conn
    except Exception as e:
        st.error(f"DB 연결 실패: {e}")
        st.stop()

# 데이터 가져오기
@st.cache_data(ttl=600)
def fetch_table(table_name):
    conn = get_db_connection()
    try:
        return conn.query(f'SELECT * FROM {table_name}')
    except Exception as e:
        st.error(f"{table_name} 테이블 로딩 실패: {e}")
        st.stop()