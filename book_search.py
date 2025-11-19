import streamlit as st
from google import genai
from google.genai import types

# Gemini 모델 초기화
@st.cache_resource
def load_gemini_client():
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        return client
    except Exception as e:
        st.error(f"Gemini 클라이언트 초기화 오류: {e}")
        return None

# 책 정보 검색 및 정리 요청
def get_ai_summary(client, book_title, book_type):
    full_query = f"책 제목: '{book_title}', 종류: '{book_type}'"
    
    # 프롬프트
    system_instruction = (
        "당신은 인공지능 책 정보 분석가입니다. "
        "사용자가 제공한 책 제목과 종류를 바탕으로, 반드시 Google Search 도구를 사용하여 최신 정보를 검색해야 합니다. "
        "검색 결과를 바탕으로 아래 **세 가지 항목만을 순서대로** 작성하여 Markdown 형식으로 반환해야 합니다. "
        "다른 추가적인 설명이나 문구는 일절 포함하지 마십시오."
        
        "### 1. 작가 및 작품 소개\n"
        "**[여기에 작가의 이름, 주요 약력, 그리고 책의 수상 경력, 판매량 등을 작성하세요.]**\n\n"
        
        "### 2. 장르 및 특징\n"
        "**[여기에 책의 주요 장르(예: 판타지, 스릴러), 문체, 핵심 주제 등의 특징을 작성하세요.]**\n\n"
        
        "### 3. 줄거리\n"
        "**[여기에 간결하고 핵심적인 줄거리 요약 내용을 작성하세요.]**\n"
        
        "절대 주관적인 의견이나 추측을 포함하지 마십시오."
        "위의 양식을 엄격히 준수하여 작성하십시요."
    )
    
    # 메세지
    prompt = f"다음 책 정보에 대해 검색하고 분석하여 정리해 주세요: {full_query}"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[{"google_search": {}}],
                temperature=0.3
            )
        )
        return response.text
    
    except Exception as e:
        return f"AI 분석 중 오류가 발생했습니다: {e}"