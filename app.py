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
from src.components.chat_message import render_sources_section

# 환경 변수 로드
load_dotenv()

# 백엔드 API 주소 환경변수 처리
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def ask_backend(question: str) -> str:
    """
    FastAPI 백엔드의 /im-fact/ask API를 호출하여 답변을 받아옵니다.
    네트워크 오류와 타임아웃에 대한 강화된 에러 핸들링 포함
    """
    try:
        # 요청 전 백엔드 상태 확인
        health_resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health_resp.status_code != 200:
            return "⚠️ 백엔드 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요."
        
        # 메인 API 호출
        resp = requests.post(
            f"{BACKEND_URL}/im-fact/ask",
            json={"content": question},
            timeout=120,  # 2분으로 연장
            headers={"Content-Type": "application/json"}
        )
        
        if resp.status_code == 200:
            content = resp.json().get("content", "")
            if content:
                return content
            else:
                return "🤖 답변을 생성하는 중 문제가 발생했습니다. 다시 시도해주세요."
        elif resp.status_code == 400:
            return "❌ 질문 형식에 문제가 있습니다. 다른 방식으로 질문해주세요."
        elif resp.status_code == 500:
            return "🔧 서버에서 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."
        else:
            return f"⚠️ 예상치 못한 오류가 발생했습니다. (상태코드: {resp.status_code})"
            
    except requests.exceptions.Timeout:
        return "⏱️ 답변 생성에 시간이 오래 걸리고 있습니다. 복잡한 질문의 경우 시간이 더 소요될 수 있습니다."
    except requests.exceptions.ConnectionError:
        return "🌐 네트워크 연결을 확인해주세요. 백엔드 서버가 실행 중인지 확인해주세요."
    except requests.exceptions.RequestException as e:
        return f"📡 요청 처리 중 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        return f"🚨 예상치 못한 오류가 발생했습니다: {str(e)}"

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
    try:
        sessions = chat_storage.get_all_sessions()
        if sessions:
            st.session_state.current_session_id = str(sessions[0]['id'])  # 문자열로 변환
            # 기존 메시지 로드
            st.session_state.chat_history = chat_storage.get_messages(sessions[0]['id'])
        else:
            st.session_state.current_session_id = str(chat_storage.create_session("새 대화"))
            st.session_state.chat_history = []
    except Exception as e:
        # 세션 초기화 실패 시 기본 오프라인 세션 생성
        import uuid
        offline_id = f"offline_{uuid.uuid4().hex[:8]}"
        st.session_state.current_session_id = offline_id
        st.session_state.chat_history = []
        st.warning("💾 오프라인 모드로 시작합니다.")
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

# 사용자 입력 처리
def handle_user_input():
    """
    사용자 입력 처리 함수 (개선된 버전)
    """
    user_input = st.session_state.chat_input
    if user_input and user_input.strip():
        # 입력 검증
        if len(user_input.strip()) < 2:
            st.warning("⚠️ 질문을 더 자세히 입력해주세요.")
            return
        
        if len(user_input) > 1000:
            st.warning("⚠️ 질문이 너무 깁니다. 1000자 이내로 입력해주세요.")
            return
        
        now = datetime.now().strftime("%H:%M")
        message = {
            "role": "user",
            "content": user_input.strip(),
            "time": now,
            "timestamp": datetime.now().isoformat()
        }
        
        # 즉시 UI에 추가
        st.session_state.chat_history.append(message)
        
        # 메시지 저장 (백엔드 API) - 실패해도 진행
        try:
            chat_storage.save_message(st.session_state.current_session_id, message)
        except Exception as save_error:
            st.warning(f"💾 메시지 저장 중 오류가 발생했습니다: {str(save_error)}")
        
        # 입력 필드 초기화
        st.session_state.chat_input = ""
        st.session_state.is_typing = True
        # st.rerun()을 콜백에서 제거 (자동으로 재실행됨)

# IM.FACT 응답 생성
def generate_response(question):
    """
    백엔드에서 응답을 생성하는 함수 (타이핑 인디케이터만 사용)
    """
    # 타이핑 효과를 위한 지연
    time.sleep(1.5)
    now = datetime.now().strftime("%H:%M")
    
    try:
        # 실제 백엔드 API 호출
        backend_answer = ask_backend(question)
        
        # 답변 검증
        if not backend_answer or backend_answer.strip() == "":
            backend_answer = "죄송합니다. 답변을 생성할 수 없었습니다. 다시 시도해주세요."
        
        answer = {
            "role": "assistant",
            "content": backend_answer,
            "time": now,
            "timestamp": datetime.now().isoformat()
        }
        
        # 채팅 기록에 응답 추가
        st.session_state.chat_history.append(answer)
        
        # 응답 저장 (백엔드 API) - 실패해도 진행
        try:
            chat_storage.save_message(st.session_state.current_session_id, answer)
        except Exception as save_error:
            st.warning(f"💾 답변 저장 중 오류가 발생했습니다: {str(save_error)}")
        
        st.session_state.is_typing = False
        
    except Exception as e:
        # 에러 처리
        error_answer = {
            "role": "assistant", 
            "content": f"🚨 답변 생성 중 오류가 발생했습니다: {str(e)}",
            "time": now,
            "timestamp": datetime.now().isoformat()
        }
        st.session_state.chat_history.append(error_answer)
        st.session_state.is_typing = False
        st.error(f"답변 생성 실패: {str(e)}")

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

    # 출처 섹션 - 출처가 있을 때만 표시
    render_sources_section()

    # 빠른 질문 버튼 렌더링
    # handle_user_input 함수를 세션 상태에 저장하여 컨포넌트에서 사용 가능하게 함
    st.session_state.handle_user_input = handle_user_input
    render_quick_buttons()

    # 검색 입력 필드 - 이전 작업물과 동일한 방식으로 복원
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
    
    # 검색 바 - 중앙 집중형 컨테이너로 감싸기
    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
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
            try:
                new_session_id = chat_storage.create_session("새 대화")
                st.session_state.current_session_id = str(new_session_id)  # 문자열로 변환
                st.session_state.chat_history = []
                st.session_state.current_tab = "home"
                # 세션 목록 업데이트
                st.session_state.sessions_list = chat_storage.get_all_sessions()
                st.query_params.tab = "home"
                st.success("✅ 새 대화가 시작되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 새 대화 생성 실패: {str(e)}")
                # 오프라인 세션으로 대체
                import uuid
                offline_id = f"offline_{uuid.uuid4().hex[:8]}"
                st.session_state.current_session_id = offline_id
                st.session_state.chat_history = []
                st.session_state.current_tab = "home"
                st.query_params.tab = "home"
                st.warning("💾 오프라인 대화로 시작합니다.")
                st.rerun()
    
    # 대화 목록 가져오기 및 정렬
    try:
        if search_query:
            sessions = chat_storage.search_sessions(search_query)
        else:
            sessions = chat_storage.get_all_sessions()
        
        # 세션 목록 유효성 검증 및 정렬
        if sessions:
            sessions = [s for s in sessions if s and 'id' in s and 'title' in s]
            sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    except Exception as e:
        st.error(f"❌ 세션 목록 로딩 실패: {str(e)}")
        sessions = []
    
    # 저장된 대화 목록 표시
    if sessions:
        for session in sessions:
            is_current_session = session['id'] == st.session_state.current_session_id
            
            # 세션 카드 컨테이너
            with st.container():
                col1, col2, col3 = st.columns([7, 1, 1])
                
                with col1:
                    # 세션 카드
                    preview_text = session.get('title', '새 대화')
                    if len(preview_text) > 50:
                        preview_text = preview_text[:50] + "..."
                    
                    # 현재 세션 표시
                    current_indicator = "🔵 " if is_current_session else ""
                    
                    # 세션 선택 버튼
                    button_type = "primary" if is_current_session else "secondary"
                    if st.button(
                        f"{current_indicator}📝 {session['title']}\n{preview_text}",
                        key=f"session_{session['id']}",
                        use_container_width=True,
                        type=button_type
                    ):
                        st.session_state.current_session_id = str(session['id'])  # 문자열로 변환
                        st.session_state.chat_history = chat_storage.get_messages(session['id'])
                        st.session_state.current_tab = "home"
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
                        try:
                            if chat_storage.delete_session(session['id']):
                                st.session_state.sessions_list = chat_storage.get_all_sessions()
                                # 현재 세션이 삭제된 경우 새 세션 생성
                                if str(st.session_state.current_session_id) == str(session['id']):  # 안전한 비교
                                    if st.session_state.sessions_list:
                                        st.session_state.current_session_id = str(st.session_state.sessions_list[0]['id'])
                                        st.session_state.chat_history = chat_storage.get_messages(st.session_state.current_session_id)
                                    else:
                                        new_session_id = chat_storage.create_session("새 대화")
                                        st.session_state.current_session_id = str(new_session_id)
                                        st.session_state.chat_history = []
                                st.success("🗑️ 대화가 삭제되었습니다.")
                                st.rerun()
                            else:
                                st.error("❌ 대화 삭제에 실패했습니다.")
                        except Exception as e:
                            st.error(f"❌ 대화 삭제 중 오류 발생: {str(e)}")
            
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
                            # update_session_title은 현재 미구현
                            st.session_state[f"editing_{session['id']}"] = False
                            st.session_state.sessions_list = chat_storage.get_all_sessions()
                            st.rerun()
            
            # 구분선
            st.markdown("---")
    else:
        st.info("저장된 대화가 없습니다. 새 대화를 시작해보세요!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 사용자 설정 탭 제거됨
    


# 푸터
st.markdown('''
<div class="imfact-footer">
    © 2025 IM.FACT - 환경・기후 전문 어시스턴트
</div>
''', unsafe_allow_html=True)

# 푸터