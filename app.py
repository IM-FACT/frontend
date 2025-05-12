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
    
    /* 채팅 메시지 컨테이너 */
    .imfact-chat-message {
        width: var(--content-width);
        max-width: var(--content-max-width);
        margin-left: auto;
        margin-right: auto;
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: 8px;
        margin-bottom: 16px;
        padding: 16px 18px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        border-left: 3px solid transparent;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .imfact-chat-message.user {
        border-left: 3px solid #4fd1c5;
        background-color: rgba(79, 209, 197, 0.05);
    }
    
    .imfact-chat-message.assistant {
        border-left: 3px solid #3B82F6;
        background-color: rgba(59, 130, 246, 0.03);
    }
    
    /* 메시지 헤더 및 아바타 */
    .message-header {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        width: 100%;
    }
    
    .avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-weight: 600;
        font-size: 14px;
    }
    
    .user-avatar {
        background: linear-gradient(135deg, #4fd1c5, #38B2AC);
        color: white;
        box-shadow: 0 2px 5px rgba(79, 209, 197, 0.4);
    }
    
    .assistant-avatar {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white;
        box-shadow: 0 2px 5px rgba(59, 130, 246, 0.4);
    }
    
    .name-title {
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .time {
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.5);
        margin-left: auto;
    }
    
    /* 인용문 스타일 강화 */
    .imfact-citation {
        background-color: rgba(79, 209, 197, 0.08);
        border-left: 3px solid var(--accent-color);
        padding: 14px 18px;
        margin: 16px 0;
        border-radius: 0 8px 8px 0;
        font-style: italic;
        position: relative;
    }
    
    .imfact-citation::before {
        content: '\201C'; /* 열린 따옴표 */
        font-size: 1.5rem;
        color: var(--accent-color);
        position: absolute;
        left: 5px;
        top: 5px;
        opacity: 0.7;
    }
    
    .imfact-citation::after {
        content: '\201D'; /* 닫힌 따옴표 */
        font-size: 1.5rem;
        color: var(--accent-color);
        position: absolute;
        right: 10px;
        bottom: 0;
        opacity: 0.7;
    }
    
    /* 키 팩트 스타일 */
    .key-fact {
        background-color: rgba(79, 209, 197, 0.1);
        border-radius: 4px;
        padding: 2px 8px;
        margin: 0 2px;
        color: #4fd1c5;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        position: relative;
    }
    
    .key-fact::before {
        content: '•'; /* 불릿 표시 */
        margin-right: 5px;
        font-size: 1.2em;
        line-height: 0;
    }
    
    /* 소스 링크 */
    .source-links {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 20px;
        margin-bottom: 10px;
        padding-top: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .source-link {
        background-color: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        padding: 5px 10px;
        font-size: 0.8rem;
        color: rgba(238, 242, 247, 0.8);
        display: inline-flex;
        align-items: center;
        transition: all 0.2s ease;
    }
    
    .source-link:hover {
        background-color: rgba(79, 209, 197, 0.1);
        border-color: rgba(79, 209, 197, 0.3);
    }
    
    .source-link span {
        margin-right: 6px;
        font-size: 1em;
    }
    
    .source-header {
        display: block;
        font-size: 0.75rem;
        color: rgba(255, 255, 255, 0.4);
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* 로딩 표시자 */
    .typing-indicator {
        display: flex;
        gap: 4px;
        margin: 8px 0;
        padding: 8px 4px;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background-color: #4fd1c5;
        border-radius: 50%;
        opacity: 0.6;
        animation: typing-animation 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) {
        animation-delay: 0s;
    }
    
    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing-animation {
        0% {
            transform: scale(1);
            opacity: 0.6;
        }
        50% {
            transform: scale(1.5);
            opacity: 1;
        }
        100% {
            transform: scale(1);
            opacity: 0.6;
        }
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

# 세션 상태 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'is_typing' not in st.session_state:
    st.session_state.is_typing = False

# 사용자 입력 처리
def handle_user_input():
    user_input = st.session_state.chat_input
    if user_input:
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "time": now
        })
        st.session_state.chat_input = ""  # 입력 필드 초기화
        st.session_state.is_typing = True
        st.rerun()

# 로고 및 환영 메시지 (처음 방문 시)
if len(st.session_state.chat_history) == 0:
    st.markdown("""
    <div class="logo-container">
        <div class="logo-text">IM.<span class="logo-highlight">FACT</span><span class="logo-badge">eco</span></div>
    </div>
    <div class="welcome-text">
        환경, 기후변화, 지속가능성에 관한 신뢰할 수 있는 정보를 제공합니다. 
        IM.FACT는 IPCC, UN환경계획, 기상청 등의 공식 자료를 기반으로 과학적이고 균형 잡힌 답변을 제공합니다.
    </div>
    """, unsafe_allow_html=True)

# 대화 기록 표시
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"""
        <div class="imfact-chat-message user">
            <div class="message-header">
                <div class="avatar user-avatar">U</div>
                <span class="name-title">You</span>
                <span class="time">{message["time"]}</span>
            </div>
            <div class="message-content">
                {message["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 소스 표시 준비
        sources_html = ""
        if "sources" in message:
            sources_html = '<div class="source-links">'
            sources_html += '<span class="source-header">출처</span>'
            for source in message["sources"]:
                sources_html += f'<div class="source-link"><span>{source["icon"]}</span> {source["name"]}</div>'
            sources_html += '</div>'
        
        # 특수 태그 변환
        content = message["content"]
        content = content.replace("<citation>", '<div class="imfact-citation">').replace("</citation>", '</div>')
        content = content.replace("<key-fact>", '<span class="key-fact">').replace("</key-fact>", '</span>')
        
        st.markdown(f"""
        <div class="imfact-chat-message assistant">
            <div class="message-header">
                <div class="avatar assistant-avatar">🌍</div>
                <span class="name-title">IM.FACT</span>
                <span class="time">{message["time"]}</span>
            </div>
            <div class="message-content">
                {content}
                {sources_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

# 타이핑 표시기
if st.session_state.is_typing:
    st.markdown("""
    <div class="imfact-chat-message assistant">
        <div class="message-header">
            <div class="avatar assistant-avatar">🌍</div>
            <span class="name-title">IM.FACT</span>
            <span class="time">응답 작성 중...</span>
        </div>
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 푸터
st.markdown('''
<div class="imfact-footer">
    © 2024 IM.FACT - 환경・기후 전문 어시스턴트 | 데이터 출처: IPCC, 기상청, UN환경계획, NASA
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # content 닫기