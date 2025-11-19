import streamlit as st
from google import genai
from google.genai import types

# Gemini 모델 초기화 함수
@st.cache_resource
def load_gemini_client():
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        return client
    except Exception as e:
        st.error(f"Gemini 클라이언트 초기화 오류: {e}")
        return None

# 책 정보 검색 및 정리 요청 함수
def get_ai_summary(client, book_title, book_type):
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
                tools=[{"google_search": {}}] 
            )
        )
        return response.text
    
    except Exception as e:
        return f"AI 분석 중 오류가 발생했습니다: {e}"