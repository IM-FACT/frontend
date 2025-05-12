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
    
    /* 사이드바 스타일 */
    .sidebar {
        position: fixed;
        top: 0;
        left: 0;
        width: 54px;
        height: 100vh;
        background-color: #0c1016;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        flex-direction: column;
        align-items: center;
        z-index: 1000;
    }
    
    .sidebar-icon {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 6px 0;
        color: rgba(255, 255, 255, 0.6);
        border-radius: 6px;
        font-size: 1.1rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .sidebar-icon:hover, .sidebar-icon.active {
        background-color: rgba(255, 255, 255, 0.08);
        color: #4fd1c5;
    }
    
    .sidebar-user {
        margin-top: auto;
        margin-bottom: 16px;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #4fd1c5, #0BC5EA);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* 메인 콘텐츠 영역 */
    .imfact-content {
        margin-left: 54px;
        width: calc(100% - 54px);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 30px 0 80px 0;
    }
    
    /* 로고 스타일 */
    .logo-container {
        text-align: center;
        margin-bottom: 30px;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .logo-text {
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    .logo-highlight {
        background: linear-gradient(135deg, #4fd1c5, #38B2AC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    .logo-badge {
        display: inline-block;
        margin-left: 6px;
        padding: 2px 6px;
        background: linear-gradient(135deg, #4fd1c5, #38B2AC);
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
        vertical-align: middle;
        text-transform: uppercase;
        color: #0c1016;
        letter-spacing: 0.5px;
    }
    
    /* 웰컴 텍스트 */
    .welcome-text {
        text-align: center;
        max-width: 600px;
        margin: 0 auto 24px;
        color: rgba(238, 242, 247, 0.7);
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* 헤더 숨기기 */
    header {
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* 사이드바 햄버거 메뉴 숨기기 */
    .st-emotion-cache-1b32qh4 {
        visibility: hidden !important;
    }
    
    /* 푸터 숨기기 */
    footer {
        visibility: hidden !important;
        height: 0 !important;
    }
    
    /* 푸터 */
    .imfact-footer {
        width: var(--content-width);
        max-width: var(--content-max-width);
        margin: 24px auto 0;
        text-align: center;
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# 사이드바
st.markdown("""
<div class="sidebar">
    <div class="sidebar-icon active" title="홈">🌍</div>
    <div class="sidebar-icon" title="기후 데이터 검색">+</div>
    <div class="sidebar-icon" title="지구 환경">🔍</div>
    <div class="sidebar-icon" title="지속가능성">🌐</div>
    <div class="sidebar-icon" title="탄소중립">♻️</div>
    <div class="sidebar-user">U</div>
</div>
""", unsafe_allow_html=True)

# 메인 콘텐츠
st.markdown('<div class="imfact-content">', unsafe_allow_html=True)

# 로고 및 환영 메시지
st.markdown("""
<div class="logo-container">
    <div class="logo-text">IM.<span class="logo-highlight">FACT</span><span class="logo-badge">eco</span></div>
</div>
<div class="welcome-text">
    환경, 기후변화, 지속가능성에 관한 신뢰할 수 있는 정보를 제공합니다. 
    IM.FACT는 IPCC, UN환경계획, 기상청 등의 공식 자료를 기반으로 과학적이고 균형 잡힌 답변을 제공합니다.
</div>
""", unsafe_allow_html=True)

# 푸터
st.markdown('''
<div class="imfact-footer">
    © 2024 IM.FACT - 환경・기후 전문 어시스턴트 | 데이터 출처: IPCC, 기상청, UN환경계획, NASA
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # content 닫기