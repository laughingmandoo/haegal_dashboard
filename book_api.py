import streamlit as st
import requests
import json

def search_naver_book(query):
    url = "https://openapi.naver.com/v1/search/book.json"
    
    headers = {
        "X-Naver-Client-Id": st.secrets["client_id"],
        "X-Naver-Client-Secret": st.secrets["client_secret"]
    }
    
    params = {
        "query": query,
        "display": 10,
        "start": 1,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        result = response.json()
        items_list = result.get("items", [])
        for item in items_list:
            title = item.get("title", "")
            if '세트' not in title:
                return item
    
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류 발생: {e}")
        return None
    
book_info = search_naver_book("블루 록 1")

if book_info:
    print("✅ 성공적으로 단권 도서 정보를 찾았습니다:")
    # 보기 쉽게 JSON 형태로 출력합니다.
    print(json.dumps(book_info, indent=4, ensure_ascii=False)) 
else:
    print("❌ '세트'가 없는 도서를 찾지 못했거나 API 오류가 발생했습니다.")