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
    
    /* 입력 필드 스타일 - Streamlit 컴포넌트 직접 스타일링 */
    .stTextInput > div {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        color: #eef2f7 !important;
    }
    
    .stTextInput > div > div > input {
        color: #eef2f7 !important;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
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
    
    /* 데이터 시각화 영역 */
    .data-visualization {
        background-color: rgba(59, 130, 246, 0.05);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: 8px;
        padding: 16px 20px;
        margin: 20px 0;
        position: relative;
    }
    
    .data-visualization::before {
        content: '📈 데이터'; /* 차트 아이콘 & 데이터 텍스트 */
        position: absolute;
        top: -10px;
        left: 15px;
        background-color: #0c1016;
        padding: 0 8px;
        font-size: 0.75rem;
        color: rgba(59, 130, 246, 0.8);
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
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
    
    /* 푸터 */
    .imfact-footer {
        width: var(--content-width);
        max-width: var(--content-max-width);
        margin: 24px auto 0;
        text-align: center;
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.8rem;
    }
    
    /* Streamlit 기본 여백 제거 */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
        margin: 0 auto !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
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
    
    /* 시각화 요소 */
    .message-content {
        width: 100%;
        line-height: 1.5;
        padding-left: 5px;
    }
    
    .message-content p {
        margin-bottom: 12px;
    }
    
    .message-content p:last-child {
        margin-bottom: 0;
    }
    
    .message-content ul, .message-content ol {
        margin-top: 8px;
        margin-bottom: 12px;
    }
    
    .message-content li {
        margin-bottom: 4px;
    }
    
    /* Streamlit 컬럼 내 버튼에 강력한 커스텀 스타일 적용 */
    .imfact-button-container [data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button,
    .stButton > button {
        background: rgba(20,25,30,0.85) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: var(--border-radius) !important;
        padding: 10px 2px !important;
        color: #eef2f7 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        white-space: nowrap !important;
        flex: 1 !important;
        min-width: 0 !important;
        width: 100% !important;
        height: 50px !important;
        line-height: normal !important;
        margin: 0 auto !important;
        overflow: hidden !important;
    }
    .imfact-button-container [data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button:hover,
    .stButton > button:hover {
        background: rgba(79,209,197,0.13) !important;
        color: var(--accent-color) !important;
        border-color: var(--accent-color) !important;
    }
    
    /* 버튼 클릭시/포커스 상태 스타일 */
    .stButton > button:active, 
    .stButton > button:focus,
    .imfact-button-container [data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button:active,
    .imfact-button-container [data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button:focus {
        background: rgba(79,209,197,0.2) !important;
        color: var(--accent-color) !important;
        border-color: var(--accent-color) !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* 검색 컨테이너 - 더 강력한 선택자 사용 */
    .imfact-search-container {
        position: relative;
        width: var(--content-width) !important;
        max-width: var(--content-max-width) !important;
        margin: 16px auto !important;
        box-sizing: border-box !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    /* 입력 필드 스타일 구체화 */
    .imfact-search-container .stTextInput {
        width: 100% !important;
        max-width: var(--content-width) !important;
        display: flex !important;
        justify-content: center !important;
    }
    
    .imfact-search-container .stTextInput > div {
        width: 100% !important;
        max-width: 100% !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: var(--border-radius) !important;
        color: #eef2f7 !important;
        padding: 0 15px !important;
    }
    
    /* 검색 아이콘 위치 조정 - 사용하지 않음 */
    /*.imfact-search-icon {
        position: absolute !important;
        left: 15px !important;
        top: 14px !important;
        color: rgba(255, 255, 255, 0.5) !important;
        z-index: 100 !important;
        font-size: 1.1rem !important;
        pointer-events: none !important;
    }*/
    
    /* 웰컴 텍스트 */
    .welcome-text {
        text-align: center;
        max-width: 600px;
        margin: 0 auto 24px;
        color: rgba(238, 242, 247, 0.7);
        font-size: 0.95rem;
        line-height: 1.5;
        margin-left: auto;
        margin-right: auto;
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    /* Streamlit 기본 스타일 오버라이드 */
    .stButton, .stTextInput {
        width: 100% !important;
        max-width: 100% !important;
        display: flex !important;
        justify-content: center !important;
    }
    /* 각 버튼 열의 너비 제한 */
    .row-widget.stButton > button {
        width: 100% !important;
        margin: 0 auto !important;
    }
    
    /* Streamlit 컬럼 정렬 개선 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        justify-content: center !important;
        gap: 2px !important;
        width: 100% !important;
        max-width: var(--content-width) !important;
        margin: 0 auto !important;
    }
    
    /* 각 컬럼의 너비와 정렬 조정 */
    [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
        flex: 1 !important;
        min-width: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* 숨겨진 버튼 스타일 */
    [data-testid="stSidebar"] [data-testid="stButton"] {
        display: none !important;
    }
    
    /* 사이드바 아이콘 클릭 효과 강화 */
    .sidebar-icon {{
        cursor: pointer !important;
        z-index: 9999 !important;
        pointer-events: auto !important;
    }}
    
    .sidebar-icon a, .sidebar-user a {{
        color: inherit;
        text-decoration: none;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
    }}
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'is_typing' not in st.session_state:
    st.session_state.is_typing = False
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "home"  # 기본 탭: 홈
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {"기본 대화": []}
if 'current_chat_session' not in st.session_state:
    st.session_state.current_chat_session = "기본 대화"

# URL 파라미터로 탭 변경 감지
if "tab" in st.query_params:
    tab_name = st.query_params["tab"]
    if tab_name in ["home", "history", "data", "sustainability", "carbon", "user"]:
        st.session_state.current_tab = tab_name

# 사이드바
st.markdown(f"""
<style>
    /* Streamlit 기본 사이드바 숨기기 */
    [data-testid="stSidebar"] {{
        display: none !important;
    }}
    
    /* 사이드바 아이콘 클릭 효과 강화 */
    .sidebar-icon {{
        cursor: pointer !important;
        z-index: 9999 !important;
        pointer-events: auto !important;
    }}
    
    .sidebar-icon a, .sidebar-user a {{
        color: inherit;
        text-decoration: none;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
    }}
</style>

<div class="sidebar">
    <div class="sidebar-icon {st.session_state.current_tab == 'home' and 'active' or ''}">
        <a href="?tab=home" title="홈" target="_self">🌍</a>
    </div>
    <div class="sidebar-icon {st.session_state.current_tab == 'history' and 'active' or ''}">
        <a href="?tab=history" title="대화 기록" target="_self">📝</a>
    </div>
    <div class="sidebar-icon {st.session_state.current_tab == 'data' and 'active' or ''}">
        <a href="?tab=data" title="지구 환경 데이터" target="_self">📊</a>
    </div>
    <div class="sidebar-icon {st.session_state.current_tab == 'sustainability' and 'active' or ''}">
        <a href="?tab=sustainability" title="지속가능성" target="_self">🌐</a>
    </div>
    <div class="sidebar-icon {st.session_state.current_tab == 'carbon' and 'active' or ''}">
        <a href="?tab=carbon" title="탄소중립" target="_self">♻️</a>
    </div>
    <div class="sidebar-user">
        <a href="?tab=user" title="사용자 설정" target="_self">👤</a>
    </div>
</div>
""", unsafe_allow_html=True)

# 메인 콘텐츠
st.markdown('<div class="imfact-content">', unsafe_allow_html=True)

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

# IM.FACT 응답 생성
def generate_response(question):
    # 타이핑 효과를 위한 지연
    time.sleep(1.5)
    
    now = datetime.now().strftime("%H:%M")
    
    # 질문에 따른 샘플 응답 (기존 코드와 동일)
    if "탄소중립" in question:
        answer = {
            "role": "assistant",
            "content": """탄소중립이란 인간 활동에 의한 온실가스 배출량을 최대한 줄이고, 남은 배출량은 산림 등의 탄소흡수원으로 제거하여 실질적인 배출량을 '0(Zero)'으로 만드는 개념입니다.

<citation>IPCC 제6차 평가보고서에 따르면, 지구온난화를 1.5℃ 이내로 제한하기 위해서는 2050년까지 전 지구적 탄소중립 달성이 필수적입니다. 현재 추세대로라면 2100년까지 지구 평균 온도가 산업화 이전 대비 3.3-5.7℃ 상승할 것으로 예측됩니다.</citation>

주요 탄소중립 달성 방안:

1. <key-fact>에너지 전환</key-fact>: 화석연료에서 재생에너지로 전환
2. <key-fact>산업구조 혁신</key-fact>: 탄소 집약적 산업의 저탄소화
3. <key-fact>흡수원 확대</key-fact>: 산림, CCUS 기술 등 탄소 제거 기술 활용

한국은 2020년 10월 '2050 탄소중립'을 선언했으며, 2021년 '기후위기 대응을 위한 탄소중립·녹색성장 기본법'을 제정했습니다. 2030년까지 2018년 대비 40% 감축을 중간목표로 설정하고 있습니다.""",
            "time": now,
            "sources": [
                {"name": "IPCC 제6차 평가보고서 (2021)", "icon": "📄"},
                {"name": "환경부 2050 탄소중립 전략", "icon": "🏛️"},
                {"name": "기후변화에 관한 정부간 협의체", "icon": "🌍"}
            ]
        }
    # 다른 질문 응답들 (기존 코드와 동일)
    else:
        answer = {
            "role": "assistant",
            "content": f"""환경 및 기후 관련 질문에 답변해 드리겠습니다. 제공해 주신 질문 "{question}"에 대한 답변입니다.

현대 환경 문제는 기후변화, 생물다양성 손실, 오염, 자원 고갈 등 다양한 측면을 포함하고 있습니다. 이러한 문제들은 서로 연결되어 있으며, 통합적인 접근이 필요합니다.

<citation>IPCC와 IPBES의 공동 보고서에 따르면, 기후변화와 생물다양성 문제는 서로 밀접하게 연관되어 있으며, 한 문제를 해결하려는 노력이 다른 문제를 악화시키지 않도록 통합적 접근법이 중요합니다.</citation>

환경 문제 해결을 위한 주요 접근법:

1. <key-fact>과학 기반 정책</key-fact>: 신뢰할 수 있는 과학적 증거에 기반한 정책 수립
2. <key-fact>시스템 사고</key-fact>: 환경, 사회, 경제적 측면을 통합적으로 고려
3. <key-fact>다자간 협력</key-fact>: 국제적, 지역적, 지방적 수준의 협력 강화

자세한 정보가 필요하시거나 특정 환경 주제에 대해 더 알고 싶으시다면, 구체적인 질문을 주시기 바랍니다.""",
            "time": now,
            "sources": [
                {"name": "IPCC-IPBES 공동 워크숍 보고서", "icon": "📄"},
                {"name": "UN 환경계획 글로벌 환경 전망", "icon": "🌐"},
                {"name": "환경부 환경정책 기본계획", "icon": "🏛️"}
            ]
        }
    
    # 채팅 기록에 응답 추가
    st.session_state.chat_history.append(answer)
    st.session_state.is_typing = False

# 탭별 콘텐츠 표시
if st.session_state.current_tab == "home":
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
            content = content.replace("<data-visualization>", '<div class="data-visualization">').replace("</data-visualization>", '</div>')
            
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
        
        # 응답 생성 및 재실행
        last_question = st.session_state.chat_history[-1]["content"]
        generate_response(last_question)
        st.rerun()

    # 버튼 컨테이너
    st.markdown('<div class="imfact-button-container">', unsafe_allow_html=True)
    cols = st.columns([0.9, 1, 0.8, 1, 1.1])

    button_definitions = [
        {"icon": "🌡️", "label": "기후변화", "key": "btn_climate_impact", "query": "기후변화가 한국에 미치는 영향은?"},
        {"icon": "♻️", "label": "탄소중립", "key": "btn_carbon_neutral", "query": "탄소중립이란 무엇인가요?"},
        {"icon": "🌐", "label": "IPCC", "key": "btn_ipcc", "query": "IPCC란 무엇인가요?"},
        {"icon": "📊", "label": "온실가스", "key": "btn_emissions", "query": "한국의 온실가스 배출 현황은?"},
        {"icon": "💪", "label": "실천방법", "key": "btn_personal", "query": "기후변화 대응 방법은?"}
    ]

    for i, button_def in enumerate(button_definitions):
        with cols[i]:
            button_text = f"{button_def['icon']} {button_def['label']}"
            if st.button(button_text, key=button_def["key"], use_container_width=True):
                st.session_state.chat_input = button_def["query"]
                handle_user_input()

    st.markdown('</div>', unsafe_allow_html=True)

    # 검색 입력 필드
    st.markdown('<div style="display: flex; justify-content: center; width: 100%; margin-top: 20px;">', unsafe_allow_html=True)
    search_container = st.container()
    with search_container:
        st.text_input(
            "환경, 기후, 지속가능성에 대해 무엇이든 물어보세요",
            placeholder="🔍 예: 탄소중립이란 무엇인가요?",
            label_visibility="collapsed",
            key="chat_input",
            on_change=handle_user_input
        )
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_tab == "history":
    # 대화 기록 탭
    st.markdown("""
    <div class="logo-container">
        <div class="logo-text">대화 <span class="logo-highlight">기록</span></div>
    </div>
    <div class="welcome-text">
        이전 대화 기록을 확인하고 계속할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)
    
    # 새 대화 버튼
    st.markdown('<div style="display: flex; justify-content: center; width: 100%; margin-top: 20px; margin-bottom: 30px;">', unsafe_allow_html=True)
    if st.button("새 대화 시작", key="new_chat_btn", use_container_width=False):
        # 새로운 대화 세션 생성
        new_session_name = f"대화 {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_session_name] = []
        st.session_state.current_chat_session = new_session_name
        st.session_state.current_tab = "home"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 저장된 대화 목록 표시
    st.markdown('<div class="chat-history-list">', unsafe_allow_html=True)
    for session_name, session_history in st.session_state.chat_sessions.items():
        # 각 대화 세션의 첫 번째 메시지나 기본 텍스트 가져오기
        preview_text = "새 대화"
        if session_history and len(session_history) > 0:
            first_user_msg = next((msg for msg in session_history if msg["role"] == "user"), None)
            if first_user_msg:
                preview_text = first_user_msg["content"][:30] + "..." if len(first_user_msg["content"]) > 30 else first_user_msg["content"]
                
        # 세션별 카드 스타일로 표시
        st.markdown(f'''
        <div class="chat-session-card" onclick="window.location.href='?tab=home&session={session_name}'" style="cursor:pointer;">
            <div class="chat-session-title">{session_name}</div>
            <div class="chat-session-preview">{preview_text}</div>
        </div>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_tab == "data":
    # 데이터 탭
    st.markdown("""
    <div class="logo-container">
        <div class="logo-text">기후 <span class="logo-highlight">데이터</span></div>
    </div>
    <div class="welcome-text">
        주요 기후 및 환경 데이터를 시각화하여 제공합니다.
    </div>
    """, unsafe_allow_html=True)
    
    # 시각화 예시 (간단한 차트)
    # 여기에 시각화 코드 추가

elif st.session_state.current_tab == "sustainability":
    # 지속가능성 탭 
    st.markdown("""
    <div class="logo-container">
        <div class="logo-text">지속<span class="logo-highlight">가능성</span></div>
    </div>
    <div class="welcome-text">
        지속가능한 미래를 위한 정보와 자원을 제공합니다.
    </div>
    """, unsafe_allow_html=True)
    
    # 추가 콘텐츠...

elif st.session_state.current_tab == "carbon":
    # 탄소중립 탭
    st.markdown("""
    <div class="logo-container">
        <div class="logo-text">탄소<span class="logo-highlight">중립</span></div>
    </div>
    <div class="welcome-text">
        탄소중립 달성을 위한 정보와 가이드를 제공합니다.
    </div>
    """, unsafe_allow_html=True)
    
    # 추가 콘텐츠...

elif st.session_state.current_tab == "user":
    # 사용자 탭
    st.markdown("""
    <div class="logo-container">
        <div class="logo-text">사용자 <span class="logo-highlight">설정</span></div>
    </div>
    <div class="welcome-text">
        개인 설정 및 대화 기록을 관리합니다.
    </div>
    """, unsafe_allow_html=True)
    
    # 추가 콘텐츠...

# 푸터
st.markdown('''
<div class="imfact-footer">
    © 2024 IM.FACT - 환경・기후 전문 어시스턴트 | 데이터 출처: IPCC, 기상청, UN환경계획, NASA
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # content 닫기