import streamlit as st
import requests
import json

def search_book(query):
    url = "https://openapi.naver.com/v1/search/book.json"
    headers = {
        "X-Naver-Client-Id": st.secrets["client_id"],
        "X-Naver-Client-Secret": st.secrets["client_secret"]
    }
    params = {
        "query": query,
        "display": 10,
        "start": 1,
        "sort" : 'count'    
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류 발생: {e}")
        return None

def search_result(title, category_name):
    category_group = {"만화": "코믹",
                      "소설": "노벨"}
    for key, items in category_group:
        if category_name == key:
            category_name = items        

    result = search_book(category_name + title)
    items_list = result.get("items", [])
    for item in items_list:
        title = item.get("title", "")
        if '세트' not in title:
            return item
    return None