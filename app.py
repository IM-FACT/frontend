import streamlit as st
import requests
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import sys

# 프로젝트 루트 디렉토리를 PATH에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.css_loader import load_css
from src.components import render_chat_message, render_typing_indicator, render_sidebar, handle_tab_change, render_quick_buttons

# 환경 변수 로드
load_dotenv()

# 페이지 구성
st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="IM.FACT - 환경 기후 어시스턴트")

# CSS 로드
load_css()

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
new_tab = handle_tab_change()
if new_tab:
    st.session_state.current_tab = new_tab

# 사이드바 렌더링
render_sidebar()

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
    # 다른 질문 응답들
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
        render_chat_message(message)

    # 타이핑 표시기
    if st.session_state.is_typing:
        render_typing_indicator()
        
        # 응답 생성 및 재실행
        last_question = st.session_state.chat_history[-1]["content"]
        generate_response(last_question)
        st.rerun()

    # 빠른 질문 버튼 렌더링
    # handle_user_input 함수를 세션 상태에 저장하여 컨포넌트에서 사용 가능하게 함
    st.session_state.handle_user_input = handle_user_input
    render_quick_buttons()

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
    © 2025 IM.FACT - 환경・기후 전문 어시스턴트 | 데이터 출처: IPCC, 기상청, UN환경계획, NASA
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # content 닫기