import streamlit as st
import requests
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import sys
import re

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
    render_tab_welcome
)
from src.components.chat_message import render_sources_section

# 환경 변수 로드
load_dotenv()

# 백엔드 API 주소 환경변수 처리 - EC2 서버 연결
BACKEND_URL = os.getenv("BACKEND_URL")

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
            timeout=240,  # 4분으로 연장
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
        # 줄바꿈 정리 (연속된 줄바꿈을 하나로, 앞뒤 공백 제거)
        cleaned_input = user_input.strip()
        # 연속된 줄바꿈을 최대 2개로 제한
        cleaned_input = re.sub(r'\n{3,}', '\n\n', cleaned_input)
        
        # 입력 검증
        if len(cleaned_input) < 2:
            st.warning("⚠️ 질문을 더 자세히 입력해주세요.")
            return
        
        if len(cleaned_input) > 2000:
            st.warning("⚠️ 질문이 너무 깁니다. 2000자 이내로 입력해주세요.")
            return
        
        now = datetime.now().strftime("%H:%M")
        message = {
            "role": "user",
            "content": cleaned_input,
            "time": now,
            "timestamp": datetime.now().isoformat()
        }
        
        # 즉시 UI에 추가
        st.session_state.chat_history.append(message)
        
        # 첫 번째 질문인 경우 세션 제목을 자동으로 질문으로 설정
        if len(st.session_state.chat_history) == 1:
            try:
                # 제목용으로 질문을 10자로 제한하고 "..." 추가
                title = cleaned_input[:13] + "..." if len(cleaned_input) > 16 else cleaned_input
                # 새 세션을 제목과 함께 생성 (기존 세션 교체)
                new_session_id = chat_storage.create_session(title)
                # 기존 임시 세션을 새 세션으로 교체
                old_session_id = st.session_state.current_session_id
                st.session_state.current_session_id = str(new_session_id)
                
                # 기존 임시/오프라인 세션이었다면 삭제
                if old_session_id.startswith("offline_"):
                    chat_storage.delete_session(old_session_id)
                    
                st.session_state.sessions_list = chat_storage.get_all_sessions()
            except Exception as title_error:
                st.warning(f"📝 세션 제목 설정 중 오류: {str(title_error)}")
        
        # 메시지 저장 (백엔드 API) - 실패해도 진행
        try:
            chat_storage.save_message(st.session_state.current_session_id, message)
        except Exception as save_error:
            st.warning(f"💾 메시지 저장 중 오류가 발생했습니다: {str(save_error)}")
        
        # 입력 필드 초기화
        st.session_state.chat_input = ""
        st.session_state.is_typing = True
        # st.rerun()을 콜백에서 제거 (자동으로 재실행됨)

def handle_textarea_keydown():
    """
    텍스트 영역 키보드 이벤트 처리를 위한 JavaScript
    Enter: 검색 실행, Shift+Enter: 줄바꿈
    자동 높이 조절 기능 포함
    """
    return """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        function autoResizeTextarea(textarea) {
            // 텍스트 영역 자동 높이 조절
            function adjustHeight() {
                // 스크롤 높이를 체크하기 위해 임시로 높이를 최소값으로 설정
                textarea.style.height = 'auto';
                
                // 실제 필요한 높이 계산
                const scrollHeight = textarea.scrollHeight;
                const minHeight = 80; // 최소 높이 (CSS와 동일)
                const maxHeight = window.innerWidth <= 767 ? 250 : 
                                 window.innerWidth <= 1024 ? 275 : 300; // 반응형 최대 높이
                
                // 최소/최대 높이 범위 내에서 조절
                const newHeight = Math.max(minHeight, Math.min(scrollHeight, maxHeight));
                textarea.style.height = newHeight + 'px';
                
                // 컨테이너 높이도 조절
                const container = textarea.closest('[data-testid="stTextArea"] > div');
                if (container) {
                    container.style.minHeight = newHeight + 'px';
                }
                
                // 최대 높이에 도달했으면 스크롤 표시
                if (scrollHeight > maxHeight) {
                    textarea.style.overflowY = 'auto';
                } else {
                    textarea.style.overflowY = 'hidden';
                }
            }
            
            // 입력 이벤트에 높이 조절 연결
            textarea.addEventListener('input', adjustHeight);
            textarea.addEventListener('paste', function() {
                setTimeout(adjustHeight, 10); // paste 후 잠시 대기
            });
            
            // 초기 높이 설정
            setTimeout(adjustHeight, 100);
            
            return adjustHeight;
        }
        
        function setupTextAreaHandlers() {
            const textareas = document.querySelectorAll('[data-testid="stTextArea"] textarea');
            
            textareas.forEach(function(textarea) {
                // 이미 핸들러가 설정되어 있으면 건너뛰기
                if (textarea.hasAttribute('data-enter-handler')) {
                    return;
                }
                textarea.setAttribute('data-enter-handler', 'true');
                
                // 자동 높이 조절 설정
                const adjustHeight = autoResizeTextarea(textarea);
                
                // 키보드 이벤트 처리
                textarea.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter') {
                        if (!e.shiftKey) {
                            // Enter만 눌렀을 때: 검색 실행
                            e.preventDefault();
                            
                            // Streamlit의 onChange 이벤트 트리거
                            const event = new Event('input', { bubbles: true });
                            textarea.dispatchEvent(event);
                            
                            // 약간의 지연 후 버튼 클릭 시뮬레이션
                            setTimeout(function() {
                                const changeEvent = new Event('change', { bubbles: true });
                                textarea.dispatchEvent(changeEvent);
                            }, 10);
                        } else {
                            // Shift+Enter: 줄바꿈 후 높이 조절
                            setTimeout(adjustHeight, 10);
                        }
                    }
                });
                
                // 창 크기 변경 시 높이 재조절
                window.addEventListener('resize', function() {
                    setTimeout(adjustHeight, 100);
                });
            });
        }
        
        // 초기 설정
        setupTextAreaHandlers();
        
        // MutationObserver로 동적 요소 감지
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    setupTextAreaHandlers();
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
    </script>
    """

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
            "timestamp": datetime.now().isoformat(),
            "sources": []  # 출처는 렌더링 시 자동 추출됨
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

    # 출처는 이제 각 메시지별로 표시됨 (render_sources_section 제거)

    # Perplexity 스타일 검색창 - Streamlit 네이티브 기능 유지, textarea로 변경
    st.markdown('<div class="perplexity-search-container">', unsafe_allow_html=True)
    
    # JavaScript로 키보드 이벤트 처리
    st.markdown(handle_textarea_keydown(), unsafe_allow_html=True)
    
    st.text_area(
        "질문을 입력하세요...",
        placeholder="기후변화에 대해 무엇이든 질문하세요",
        label_visibility="collapsed",
        key="chat_input",
        on_change=handle_user_input,
        height=80,  # 기본 높이 늘림
        max_chars=2000  # 최대 글자 수 제한
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_tab == "history":
    # 대화 기록 탭
    render_tab_welcome("history")
    
    # 검색 바 - 중앙 집중형 컨테이너로 감싸기
    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
    
    # 검색창을 전체 너비로 사용
    search_query = st.text_input(
        "대화 검색",
        placeholder="🔍 대화 검색",
        key="search_history",
        label_visibility="collapsed"
    )
    
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
            
            # 세션 카드 컨테이너 - 2컬럼으로 최적화
            with st.container():
                col1, col2 = st.columns([6, 1])
                
                with col1:
                    # 세션 카드
                    session_title = session.get('title', '새 대화')
                    
                    # 메시지 개수와 시간 정보로 미리보기 생성
                    messages = chat_storage.get_messages(session['id'])
                    if messages:
                        message_count = len(messages)
                        created_at = session.get('created_at', '')
                        if created_at and 'T' in created_at:
                            date_part = created_at.split('T')[0]
                            preview_text = f"{message_count}개 메시지 • {date_part}"
                        else:
                            preview_text = f"{message_count}개 메시지"
                    else:
                        preview_text = "빈 대화"
                    
                    # 현재 세션 표시
                    current_indicator = "🔵 " if is_current_session else ""
                    
                    # 세션 선택 버튼 - 제목과 메타 정보 분리
                    button_type = "primary" if is_current_session else "secondary"
                    if st.button(
                        f"{current_indicator}📝 {session_title}\n💬 {preview_text}",
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
                    # 삭제 버튼 - 더 큰 크기로 개선
                    if st.button("🗑️ 삭제", key=f"delete_{session['id']}", help="대화 삭제", use_container_width=True):
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
            
            # 제목 편집 기능 제거 - 첫 번째 질문이 자동으로 제목이 됨
            
            # 구분선 제거 - CSS 마진으로 충분한 간격 확보
    else:
        st.info("저장된 대화가 없습니다. 새 대화를 시작해보세요!")
    
    # 새 대화 버튼을 하단에 배치
    st.markdown("---")
    if st.button("➕ 새 대화 시작", key="new_chat_btn", use_container_width=True, type="primary"):
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
    
    st.markdown('</div>', unsafe_allow_html=True)

# 사용자 설정 탭 제거됨
    


# 푸터
st.markdown('''
<div class="imfact-footer">
    © 2025 IM.FACT - 환경・기후 전문 어시스턴트
</div>
''', unsafe_allow_html=True)

# 푸터