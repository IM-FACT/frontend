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
from src.utils.chat_storage import chat_storage
from src.utils.user_settings import user_settings
from src.components import (
    render_chat_message, 
    render_typing_indicator, 
    render_sidebar, 
    handle_tab_change, 
    render_quick_buttons,
    render_tab_welcome
)

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
if 'current_session_id' not in st.session_state:
    # 기존 세션이 있으면 가장 최근 세션, 없으면 새 세션 생성
    sessions = chat_storage.get_all_sessions()
    if sessions:
        st.session_state.current_session_id = sessions[0]['id']
        # 기존 메시지 로드
        st.session_state.chat_history = chat_storage.get_messages(sessions[0]['id'])
    else:
        st.session_state.current_session_id = chat_storage.create_session("새 대화")
if 'sessions_list' not in st.session_state:
    st.session_state.sessions_list = chat_storage.get_all_sessions()

# URL 파라미터로 탭 변경 감지
new_tab = handle_tab_change()
if new_tab:
    st.session_state.current_tab = new_tab

# 디버깅: 현재 탭 확인
# st.write(f"Debug - Current tab: {st.session_state.current_tab}")

# 사이드바 렌더링
render_sidebar()

# 메인 콘텐츠
st.markdown('<div class="imfact-content">', unsafe_allow_html=True)

# 사용자 입력 처리
def handle_user_input():
    user_input = st.session_state.chat_input
    if user_input:
        now = datetime.now().strftime("%H:%M")
        message = {
            "role": "user",
            "content": user_input,
            "time": now
        }
        st.session_state.chat_history.append(message)
        
        # 메시지 저장
        chat_storage.save_message(st.session_state.current_session_id, message)
        
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
    
    # 응답 저장
    chat_storage.save_message(st.session_state.current_session_id, answer)
    
    st.session_state.is_typing = False

# 탭별 콘텐츠 표시
if st.session_state.current_tab == "home":
    # 로고 및 환영 메시지 (처음 방문 시)
    if len(st.session_state.chat_history) == 0:
        render_tab_welcome("home")

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
    render_tab_welcome("history")
    
    # 검색 바
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input(
            "대화 검색",
            placeholder="🔍 대화 내용 검색...",
            key="search_history",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("새 대화", key="new_chat_btn", use_container_width=True):
            # 새로운 대화 세션 생성
            new_session_id = chat_storage.create_session()
            st.session_state.current_session_id = new_session_id
            st.session_state.chat_history = []
            st.session_state.current_tab = "home"
            # 세션 목록 업데이트
            st.session_state.sessions_list = chat_storage.get_all_sessions()
            # URL 파라미터 업데이트하여 홈 탭으로 이동
            st.query_params.tab = "home"
            st.rerun()
    
    # 대화 목록 가져오기
    if search_query:
        sessions = chat_storage.search_sessions(search_query)
    else:
        sessions = chat_storage.get_all_sessions()
    
    # 저장된 대화 목록 표시
    if sessions:
        for session in sessions:
            # 현재 활성 세션인지 확인
            is_current_session = session['id'] == st.session_state.current_session_id
            
            # 세션 카드 컨테이너
            with st.container():
                col1, col2, col3 = st.columns([7, 1, 1])
                
                with col1:
                    # 세션 카드
                    preview_text = session.get('first_message', '새 대화') or '새 대화'
                    if len(preview_text) > 50:
                        preview_text = preview_text[:50] + "..."
                    
                    # 현재 세션 표시
                    current_indicator = "🔵 " if is_current_session else ""
                    
                    # 세션 선택 버튼
                    button_type = "primary" if is_current_session else "secondary"
                    if st.button(
                        f"{current_indicator}📝 {session['title']}\n{preview_text}\n💬 {session['message_count']}개 메시지 · 📅 {session['updated_at'][:10]}",
                        key=f"session_{session['id']}",
                        use_container_width=True,
                        type=button_type
                    ):
                        # 세션 로드
                        st.session_state.current_session_id = session['id']
                        st.session_state.chat_history = chat_storage.get_messages(session['id'])
                        st.session_state.current_tab = "home"
                        # URL 파라미터 업데이트하여 홈 탭으로 이동
                        st.query_params.tab = "home"
                        st.rerun()
                
                with col2:
                    # 제목 편집 버튼
                    if st.button("✏️", key=f"edit_{session['id']}", help="제목 편집"):
                        st.session_state[f"editing_{session['id']}"] = True
                        st.rerun()
                
                with col3:
                    # 삭제 버튼
                    if st.button("🗑️", key=f"delete_{session['id']}", help="대화 삭제"):
                        if chat_storage.delete_session(session['id']):
                            st.session_state.sessions_list = chat_storage.get_all_sessions()
                            # 현재 세션이 삭제된 경우 새 세션 생성
                            if st.session_state.current_session_id == session['id']:
                                if st.session_state.sessions_list:
                                    st.session_state.current_session_id = st.session_state.sessions_list[0]['id']
                                    st.session_state.chat_history = chat_storage.get_messages(st.session_state.current_session_id)
                                else:
                                    st.session_state.current_session_id = chat_storage.create_session("새 대화")
                                    st.session_state.chat_history = []
                            st.rerun()
            
            # 제목 편집 모드
            if st.session_state.get(f"editing_{session['id']}", False):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        new_title = st.text_input(
                            "새 제목",
                            value=session['title'],
                            key=f"title_input_{session['id']}",
                            label_visibility="collapsed"
                        )
                    with col2:
                        if st.button("저장", key=f"save_title_{session['id']}"):
                            chat_storage.update_session_title(session['id'], new_title)
                            st.session_state[f"editing_{session['id']}"] = False
                            st.session_state.sessions_list = chat_storage.get_all_sessions()
                            st.rerun()
            
            # 구분선
            st.markdown("---")
    else:
        st.info("저장된 대화가 없습니다. 새 대화를 시작해보세요!")

elif st.session_state.current_tab == "data":
    # 데이터 탭
    render_tab_welcome("data")
    
    # 시각화 예시 (간단한 차트)
    # 여기에 시각화 코드 추가

elif st.session_state.current_tab == "sustainability":
    # 지속가능성 탭 
    render_tab_welcome("sustainability")
    
    # 추가 콘텐츠...

elif st.session_state.current_tab == "carbon":
    # 탄소중립 탭
    render_tab_welcome("carbon")
    
    # 추가 콘텐츠...

elif st.session_state.current_tab == "user":
    # 사용자 탭
    render_tab_welcome("user")
    
    # 현재 설정 로드
    settings = user_settings.get_all_settings()
    
    st.markdown("### 프로필 설정")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # 아바타 이모지 선택
        avatar_options = ["👤", "🌱", "🌍", "🌿", "🌊", "☀️", "🌳", "🦋", "🐧", "🐢"]
        current_avatar = settings["profile"]["avatar_emoji"]
        
        st.markdown("**아바타**")
        selected_avatar = st.selectbox(
            "아바타 선택",
            options=avatar_options,
            index=avatar_options.index(current_avatar) if current_avatar in avatar_options else 0,
            key="avatar_select",
            label_visibility="collapsed"
        )
        
        # 선택된 아바타 미리보기
        st.markdown(f"<div style='text-align: center; font-size: 60px; margin: 20px;'>{selected_avatar}</div>", unsafe_allow_html=True)
    
    with col2:
        # 닉네임
        nickname = st.text_input(
            "닉네임",
            value=settings["profile"]["nickname"],
            key="nickname_input",
            placeholder="닉네임을 입력하세요"
        )
        
        # 자기소개
        bio = st.text_area(
            "자기소개",
            value=settings["profile"]["bio"],
            key="bio_input",
            placeholder="환경에 관심이 있는 이유나 목표를 공유해주세요",
            height=100
        )
        
        # 프로필 저장 버튼
        if st.button("프로필 저장", key="save_profile", type="primary"):
            user_settings.update_category("profile", {
                "nickname": nickname,
                "bio": bio,
                "avatar_emoji": selected_avatar
            })
            st.success("프로필이 저장되었습니다!")
    
    # 향후 확장 가능한 설정들을 위한 공간
    st.markdown("---")
    st.markdown("### 개발 예정 기능")
    
    with st.expander("🛠️ 향후 추가될 기능들"):
        st.info("""
        - **테마 설정**: 라이트/다크 모드 선택
        - **언어 설정**: 한국어/영어 지원
        - **응답 스타일**: 간단한 답변부터 학술적 설명까지
        - **대화 기록 관리**: 자동 저장, 내보내기 기능
        - **데이터 시각화 커스터마이징**
        """)
    
    # 환경설정 주석 처리 (나중에 활성화 가능)
    # col1, col2 = st.columns(2)
    # 
    # with col1:
    #     # 테마 설정
    #     st.markdown("**테마**")
    #     theme = st.radio(
    #         "테마 선택",
    #         options=["light", "dark"],
    #         format_func=lambda x: "🌞 라이트 모드" if x == "light" else "🌙 다크 모드",
    #         index=0 if settings["preferences"]["theme"] == "light" else 1,
    #         key="theme_radio",
    #         label_visibility="collapsed"
    #     )
    #     
    #     # 언어 설정
    #     st.markdown("**언어**")
    #     language = st.selectbox(
    #         "언어 선택",
    #         options=["ko", "en"],
    #         format_func=lambda x: "🇰🇷 한국어" if x == "ko" else "🇺🇸 English",
    #         index=0 if settings["preferences"]["language"] == "ko" else 1,
    #         key="language_select",
    #         label_visibility="collapsed"
    #     )
    # 
    # with col2:
    #     # 응답 스타일
    #     st.markdown("**응답 스타일**")
    #     response_style = st.radio(
    #         "응답 스타일",
    #         options=["simple", "detailed", "academic"],
    #         format_func=lambda x: {
    #             "simple": "🎯 간단명료",
    #             "detailed": "📋 상세설명",
    #             "academic": "🎓 학술적"
    #         }[x],
    #         index=["simple", "detailed", "academic"].index(settings["preferences"]["response_style"]),
    #         key="response_style_radio",
    #         label_visibility="collapsed"
    #     )

# 푸터
st.markdown('''
<div class="imfact-footer">
    © 2025 IM.FACT - 환경・기후 전문 어시스턴트 | 데이터 출처: IPCC, 기상청, UN환경계획, NASA
</div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # content 닫기