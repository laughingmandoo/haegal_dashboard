import streamlit as st
import pandas as pd
from db import fetch_table

series_df = fetch_table("series")
category_df = fetch_table("category")
book_df = fetch_table("book")
alias_df = fetch_table("alias")

# 대시보드 UI

# 사이드바
st.sidebar.title("필터 옵션 (작동X)")

# 1. 카테고리 필터
category_list = category_df['category_name']
selected_category = st.sidebar.multiselect("카테고리 선택:", category_list)

# 2. 대여 가능 필터
rentable = st.sidebar.checkbox("대여 가능한 책만 보기")

# 3. 데이터 새로고침
refresh = st.sidebar.button("데이터 새로고침")
if refresh:
    st.cache_data.clear()
    st.rerun()

# 메인 화면
st.title("해갈 도서관 DB")

# 1. 기초 통계
total_books = len(book_df)
rentable_books = len(book_df[book_df['can_rent'] == True])

col1, col2 = st.columns(2)
col1.metric("총 보유 권수", f"{total_books} 권")
col2.metric("대여 가능 권수", f"{rentable_books} 권")

# 2. 도서 목록
st.subheader("도서 목록")
st.dataframe(book_df.sort_values('book_code'))

# 3. 위치별 책 수
st.subheader("위치별 보유 현황")
location_counts = book_df['location'].value_counts()
st.bar_chart(location_counts)