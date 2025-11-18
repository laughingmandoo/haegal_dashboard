import streamlit as st
import pandas as pd
import altair as alt
from db import fetch_table

series_df = fetch_table("series")
category_df = fetch_table("category")
book_df = fetch_table("book")
alias_df = fetch_table("alias")

# 대시보드 UI

# 사이드바
st.sidebar.title("도서 검색 & 필터")

# - 통합 검색
search_keyword = st.sidebar.text_input("통합 검색", placeholder="제목 / 시리즈 / 별칭")

# - 카테고리 필터
category_list = category_df['category_name']
selected_category = st.sidebar.multiselect("카테고리 선택:", category_list, placeholder="카테고리")

# - 대여 가능 필터
rentable = st.sidebar.checkbox("대여 가능한 책만 보기")

st.sidebar.divider()

# - 데이터 새로고침
refresh = st.sidebar.button("새로고침")
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

# 필터링
filtered_book_df = book_df.copy()

# 검색
if search_keyword:
    series_matches = series_df[series_df['series_name'].str.contains(search_keyword, case=False)]['series_id']
    alias_matches = alias_df[alias_df['alias_name'].str.contains(search_keyword, case=False)]['series_id']
    target_series_ids = set(series_matches) | set(alias_matches)

    filtered_book_df = filtered_book_df[(filtered_book_df['title'].str.contains(search_keyword, case=False)) | (filtered_book_df['series_id'].isin(target_series_ids))]

# 카테고리
if selected_category:
    selected_id = category_df[category_df['category_name'].isin(selected_category)]['category_id']
    filtered_book_df = filtered_book_df[filtered_book_df['category_id'].isin(selected_id)]
    
# 대여 가능
if rentable:
    filtered_book_df = filtered_book_df[filtered_book_df['can_rent'] == True]


st.divider()

# 2. 도서 목록
st.subheader("도서 목록")
if not filtered_book_df.empty:
    st.dataframe(filtered_book_df[['book_code','title','location','can_rent']].sort_values('book_code'))
else:    
    st.info("선택한 조건에 맞는 도서가 없습니다.")

st.divider()

# 3. 위치별 책 수
st.subheader("위치별 보유 현황")
if not filtered_book_df.empty:
    filtered_book_df['zone'] = filtered_book_df['location'].str.split('-').str[0]
    zone_counts = filtered_book_df['zone'].value_counts()
    all_zones = zone_counts.index.tolist()
    
    special_zone_id = ['BA','CT','OD']    
    normal_zones = sorted([zone for zone in all_zones if zone not in special_zone_id])
    special_zones = sorted([zone for zone in all_zones if zone in special_zone_id])
    sort_order = normal_zones + special_zones
    
    chart_df = zone_counts.reindex(sort_order).reset_index()
    chart_df.columns = ['zone', 'count']
    chart = alt.Chart(chart_df).mark_bar().encode(
        x=alt.X('count', title=None),
        y=alt.Y('zone', sort=sort_order, title=None),
        tooltip=['zone', 'count']
    )
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("선택한 조건에 맞는 도서가 없습니다.")