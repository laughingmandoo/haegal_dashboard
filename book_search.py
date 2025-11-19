import streamlit as st
from google import genai
from google.genai import types

# 1. Gemini 모델 초기화 함수 (@st.cache_resource를 사용하여 재로드 방지)
@st.cache_resource
def load_gemini_client():
    # secrets.toml에 키가 없으면 실행 중단
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("🚨 Gemini API 키를 찾을 수 없습니다.")
        st.warning("`.streamlit/secrets.toml` 파일에 'GEMINI_API_KEY = \"YOUR_API_KEY\"' 형식으로 키를 설정해주세요.")
        return None

    try:
        # API 클라이언트 초기화
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        return client
    except Exception as e:
        st.error(f"Gemini 클라이언트 초기화 오류: {e}")
        return None

# 2. 책 정보 검색 및 정리 요청 함수
def get_ai_summary(client, book_title, book_type):
    """Gemini 모델을 호출하여 검색을 요청하고 결과를 받습니다."""
    
    full_query = f"책 제목: '{book_title}', 종류: '{book_type}'"
    
    # 시스템 프롬프트: 모델의 역할과 목표를 명확하게 정의
    system_instruction = (
        "당신은 인공지능 책 정보 분석가입니다. "
        "사용자가 제공한 책 제목과 종류를 바탕으로, 반드시 Google Search 도구를 사용하여 최신 정보를 검색해야 합니다. "
        "검색 결과를 바탕으로 책의 '줄거리 요약', '작가 및 특징', '사회적 영향(수상/판매량)' 세 가지 항목으로 구분하여 "
        "가장 관련성 높고 정확하게 한국어로 정리하여 Markdown 형식으로 반환하세요. "
        "절대 주관적인 의견이나 추측을 포함하지 마십시오."
    )
    
    # 모델에 전달할 메시지
    prompt = f"다음 책 정보에 대해 검색하고 분석하여 정리해 주세요: {full_query}"
    
    try:
        # Gemini API 호출 (gemini-2.5-flash 모델, Google Search 도구 활성화)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                # Google Search 도구 사용을 명시적으로 활성화
                tools=[{"google_search": {}}] 
            )
        )
        return response.text
    
    except Exception as e:
        return f"AI 분석 중 오류가 발생했습니다: {e}"


# 3. Streamlit 대시보드 UI 구성
def main():
    st.set_page_config(page_title="📚 AI 기반 책 정보 분석 서비스", layout="wide")
    st.title("📖 Gemini AI 기반 책 정보 분석 서비스")
    st.markdown("---")
    
    client = load_gemini_client()
    if not client:
        return # API 키 오류 시 실행 중단

    # 사이드바 입력 폼
    with st.sidebar:
        st.header("🔍 검색 조건 입력")
        
        book_title = st.text_input("**책 제목 (필수)**", placeholder="예: 데미안")
        book_type_options = ["소설", "만화", "에세이", "자기계발", "IT/컴퓨터", "인문학", "기타"]
        selected_type = st.selectbox("**책 종류 (선택)**", book_type_options)
        
        search_button = st.button("🚀 AI 분석 및 정리 시작")
        
        st.markdown("---")
        st.caption("✨ Gemini 모델이 Google 검색을 사용하여 정보를 찾고 분석합니다.")

    
    # 검색 버튼 클릭 시 로직 처리
    if search_button:
        if not book_title:
            st.error("책 제목을 입력해 주세요.")
            return

        with st.spinner(f"'{book_title} {selected_type}'에 대한 AI 분석 및 정리 중..."):
            # 4. API 호출 및 결과 반환
            analysis_result = get_ai_summary(client, book_title, selected_type)
            
            # 5. 결과 표시
            st.header(f"📚 {book_title} ({selected_type}) 분석 결과")
            st.markdown("---")
            st.markdown(analysis_result)
            
            st.success("✅ 분석이 완료되었습니다.")


if __name__ == "__main__":
    main()