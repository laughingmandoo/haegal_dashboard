import streamlit as st
import pandas as pd
import altair as alt
from db import fetch_table
from book_search import load_gemini_client, get_ai_summary

# 데이터 불러오기
series_df = fetch_table("series")
category_df = fetch_table("category")
book_df = fetch_table("book")
alias_df = fetch_table("alias")

# 대시보드
st.set_page_config(page_title="해갈 도서관", layout="wide")

# 사이드바
with st.sidebar:
    st.header("도서 검색 및 필터")

    # - 통합 검색
    search_keyword = st.text_input("통합 검색", placeholder="도서 제목 / 시리즈 / 별칭")
    
    # - 카테고리 필터
    category_list = category_df['category_name']
    selected_category = st.multiselect("카테고리 선택:", category_list, placeholder="카테고리")

    # - 대여 가능 필터
    rentable = st.checkbox("대여 가능한 책만 보기")
    
    # - 데이터 새로고침
    refresh = st.button("도서 목록 새로고침", width='stretch')
    if refresh:
        st.cache_data.clear()
        st.rerun()

    st.divider()

    st.header("AI 도서 소개")
    ai_book_code = st.text_input("코드 입력 :", placeholder=" 도서 코드")
    ai_search_button = st.button("AI 분석 및 정리 시작", width='stretch')


# 필터링
filtered_book_df = book_df.copy()

# 검색 필터링
if search_keyword:
    series_matches = series_df[series_df['series_name'].str.contains(search_keyword, case=False)]['series_id']
    alias_matches = alias_df[alias_df['alias_name'].str.contains(search_keyword, case=False)]['series_id']
    target_series_ids = set(series_matches) | set(alias_matches)

    filtered_book_df = filtered_book_df[(filtered_book_df['title'].str.contains(search_keyword, case=False)) | (filtered_book_df['series_id'].isin(target_series_ids))]

# 카테고리 필터링
if selected_category:
    selected_id = category_df[category_df['category_name'].isin(selected_category)]['category_id']
    filtered_book_df = filtered_book_df[filtered_book_df['category_id'].isin(selected_id)]
    
# 대여 가능 필터링
if rentable:
    filtered_book_df = filtered_book_df[filtered_book_df['can_rent'] == True]

# 메인 화면
st.title("해갈 도서관")

# 도서 정보 컨테이너
st.title("도서 정보")
with st.container(border=0):
    col1, col2, col3, = st.columns([1,1,3])

# - 기초 통계
with col1:
    st.subheader("통계")
    st.metric("총 보유 권수", f"{len(book_df)} 권")
    st.metric("검색 결과 권수", f"{len(filtered_book_df)} 권")
    
with col2:
    st.subheader("")
    col2.metric("총 대여 가능 권수", f"{len(book_df[book_df['can_rent'] == True])} 권")
    col2.metric("검색 결과 중 대여 가능 권수", f"{len(filtered_book_df[filtered_book_df['can_rent'] == True])} 권")

# - 카테고리별 도서 수
with col3:
    st.subheader("카테고리별 도서 수")
    
    book_merge_df = pd.merge(book_df, category_df[['category_id', 'category_name']], on='category_id', how='left')
    
    category_counts = book_merge_df['category_name'].value_counts().reset_index()
    category_counts.columns = ['category_name', 'count']
    category_counts['dummy'] = '전체'
    
    chart = alt.Chart(category_counts).mark_bar().encode(
        y=alt.Y('dummy', axis=None),
        x=alt.X('count', stack='normalize', title=None),
        color=alt.Color('category_name', title=None),
        tooltip=['category_name:N', 'count']
    ).properties(
        width=600,
        height=200
    ).configure_legend(
        orient='bottom',
        direction='horizontal',
        titleOrient='bottom'
    )

    st.altair_chart(chart, width="stretch")

st.divider()

# 검색 결과 컨테이너
st.header("검색 및 필터 결과")
with st.container(border=0):
    col_table, col_chart = st.columns([3, 2], gap="large")

# - 도서 목록
with col_table:
    st.subheader("도서 목록")
    
    if not filtered_book_df.empty:
        filtered_book_table_df = filtered_book_df[['book_code','title','location','can_rent']].sort_values('book_code')
        st.dataframe(filtered_book_table_df, height='stretch')
    else:    
        st.info("선택한 조건에 맞는 도서가 없습니다.")

# - 위치별 도서 수
with col_chart:
    st.subheader("위치별 도서 수")
    
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
        
        st.altair_chart(chart, width='content', height='stretch')
    else:
        st.info("선택한 조건에 맞는 도서가 없습니다.")

st.divider()

# AI 도서 소개 컨테이너
st.header("AI 도서 소개")
ai_container = st.container(border=0)

if 'ai_analysis_done' not in st.session_state:
    st.session_state.ai_analysis_done = False
    
if not st.session_state.ai_analysis_done:
    ai_container.info("사이드바에 도서 코드를 입력하고 'AI 분석 및 정리 시작' 버튼을 눌러주세요.")

st.session_state.ai_analysis_done = True

client = load_gemini_client()

# - AI 도서 소개
if ai_search_button:
    ai_container.empty()
    
    with ai_container:
        if not ai_book_code:
            st.error("도서 코드를 입력해 주세요.")
            st.stop()
        
        book_data = book_merge_df[book_merge_df['book_code'] == ai_book_code]
        if book_data.empty:
            st.error(f"도서 코드 '{ai_book_code}'에 해당하는 도서를 찾을 수 없습니다.")
            st.stop()
            
        ai_title = book_data['title'].item()
        ai_category_name = book_data['category_name'].item()
        
        with st.spinner(f"'\[{ai_book_code}\] {ai_title} ({ai_category_name})'에 대한 AI 분석 및 정리 중.."):
            analysis_result = get_ai_summary(client, ai_title, ai_category_name)
            
            
            if analysis_result is None or 'AI 분석 중 오류가 발생했습니다' in analysis_result:
                st.error(f"검색 실패: {analysis_result if analysis_result else '검색 결과를 찾을 수 없습니다.'}")
                st.warning("잠시 후 다시 시도하거나, 도서 코드와 API 키 설정을 확인해 주세요.")
            else:
                st.subheader(f"\[{ai_book_code}\] {ai_title} ({ai_category_name}) 검색 결과")
                with st.container(border=1):
                    st.markdown(analysis_result)
                st.success("분석이 완료되었습니다.")