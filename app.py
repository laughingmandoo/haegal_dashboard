import streamlit as st
import pandas as pd

# 1. DB 연결 (secrets.toml에 정의된 "supabase_db" 이름을 사용)
try:
    conn = st.connection("supabase_db", type="sql")
except Exception as e:
    st.error(f"DB 연결 실패: {e}")
    st.info("'.streamlit/secrets.toml' 파일에 연결 정보가 올바른지 확인하세요.")
    st.stop() # 연결 실패 시 앱 실행 중지

# 2. 데이터 가져오는 함수 (캐시 사용)
@st.cache_data(ttl=600) # 600초(10분)마다 캐시 갱신
def fetch_data(table_name):
    try:
        df = conn.query(f"SELECT * FROM {table_name};")
        return df
    except Exception as e:
        st.error(f"'{table_name}' 테이블 로딩 실패: {e}")
        return pd.DataFrame() # 오류 발생 시 빈 DataFrame 반환

# --- 📚 대시보드 UI 그리기 ---
st.title("내 서재 대시보드 (from Supabase) 🚀")

# 3. 'series' 테이블 데이터 가져와서 표시
st.subheader("1. 시리즈 목록")
series_df = fetch_data("series")
if not series_df.empty:
    st.dataframe(series_df)
else:
    st.warning("'series' 테이블에 데이터가 없거나 로드에 실패했습니다.")

# 4. 'book' 테이블 데이터 가져와서 표시
st.subheader("2. 전체 도서 목록")
book_df = fetch_data("book")
if not book_df.empty:
    st.dataframe(book_df)
else:
    st.warning("'book' 테이블에 데이터가 없거나 로드에 실패했습니다.")