import streamlit as st
import requests
from dotenv import load_dotenv
import os
import time
from datetime import datetime

# 환경 변수 로드
load_dotenv()

# 페이지 구성
st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="IM.FACT - 환경 기후 어시스턴트")

# 기후 특화 테마 적용 (순수 CSS만 사용)
st.markdown("""
<style>
    /* 공통 너비 변수 정의 */
    :root {
        --content-width: 650px;
        --content-max-width: 90%;
        --border-radius: 18px;
        --accent-color: #4fd1c5;
    }
    /* 글로벌 스타일 */
    html, body, .main, .stApp {
        background-color: #0c1016 !important;
        color: #eef2f7 !important;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }
    
    /* 메인 콘텐츠 영역 */
    .imfact-content {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px 0 80px 0;
    }
    
    /* 헤더 숨기기 */
    header {
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* 푸터 숨기기 */
    footer {
        visibility: hidden !important;
        height: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# 메인 콘텐츠
st.markdown('<div class="imfact-content">', unsafe_allow_html=True)

st.write("IM.FACT - 환경 기후 어시스턴트")

st.markdown('</div>', unsafe_allow_html=True)  # content 닫기