"""
채팅 기록 저장 및 관리 유틸리티
JSON 파일로 대화 기록을 영구 저장하고 관리합니다.
"""
import requests
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")

class ChatStorage:
    """
    백엔드 API를 통해 채팅 세션/메시지를 관리하는 클래스
    네트워크 오류에 대한 강화된 처리와 오프라인 지원 포함
    """
    def __init__(self):
        self.backend_url = BACKEND_URL
        self._offline_cache = {}
        self._connection_status = True

    def _is_backend_available(self) -> bool:
        """백엔드 서버 연결 상태를 확인합니다."""
        try:
            resp = requests.get(f"{self.backend_url}/health", timeout=3)
            self._connection_status = resp.status_code == 200
            return self._connection_status
        except:
            self._connection_status = False
            return False

    def _handle_api_error(self, operation: str, error: Exception):
        """API 오류를 처리하고 사용자에게 적절한 피드백을 제공합니다."""
        import streamlit as st
        
        if isinstance(error, requests.exceptions.ConnectionError):
            st.warning(f"🌐 {operation} 중 연결 오류가 발생했습니다. 네트워크 연결을 확인해주세요.")
        elif isinstance(error, requests.exceptions.Timeout):
            st.warning(f"⏱️ {operation} 중 시간 초과가 발생했습니다. 잠시 후 다시 시도해주세요.")
        elif isinstance(error, requests.exceptions.RequestException):
            st.error(f"📡 {operation} 중 요청 오류가 발생했습니다: {str(error)}")
        else:
            st.error(f"🚨 {operation} 중 예상치 못한 오류가 발생했습니다: {str(error)}")

    def create_session(self, title: Optional[str] = None) -> str:
        """세션 생성 (오프라인 대응 포함)"""
        import uuid
        import streamlit as st
        
        payload = {"title": title or f"대화 {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
        
        if not self._is_backend_available():
            # 오프라인 모드: 임시 세션 ID 생성
            temp_id = f"offline_{uuid.uuid4().hex[:8]}"
            self._offline_cache[temp_id] = {
                "id": temp_id,
                "title": payload["title"],
                "created_at": datetime.now().isoformat(),
                "messages": []
            }
            st.info("📱 오프라인 모드: 임시 세션이 생성되었습니다.")
            return temp_id
        
        try:
            resp = requests.post(f"{self.backend_url}/chat/sessions", json=payload, timeout=10)
            if resp.status_code == 200:
                return str(resp.json()["id"])
            else:
                st.error(f"❌ 세션 생성 실패: HTTP {resp.status_code}")
                raise Exception(f"세션 생성 실패: {resp.text}")
        except Exception as e:
            self._handle_api_error("세션 생성", e)
            raise e

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """세션 목록 조회 (오프라인 캐시 포함, 데이터 정합성 강화)"""
        import streamlit as st
        
        # 오프라인 캐시 세션도 포함
        offline_sessions = []
        for session in self._offline_cache.values():
            if isinstance(session, dict) and 'id' in session and 'title' in session:
                offline_sessions.append(session)
        
        if not self._is_backend_available():
            st.info("📱 오프라인 모드: 캐시된 세션만 표시됩니다.")
            return offline_sessions
        
        try:
            resp = requests.get(f"{self.backend_url}/chat/sessions", timeout=10)
            if resp.status_code == 200:
                backend_sessions = resp.json()
                # 데이터 유효성 검증
                valid_sessions = []
                for session in backend_sessions:
                    if isinstance(session, dict) and 'id' in session and 'title' in session:
                        # created_at이 없으면 기본값 설정
                        if 'created_at' not in session:
                            session['created_at'] = '1970-01-01T00:00:00'
                        valid_sessions.append(session)
                
                # 최신순 정렬 (created_at 기준)
                valid_sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                # 오프라인 세션과 합치기
                return valid_sessions + offline_sessions
            else:
                st.warning(f"⚠️ 세션 목록 조회 오류: HTTP {resp.status_code}")
                return offline_sessions
        except Exception as e:
            self._handle_api_error("세션 목록 조회", e)
            return offline_sessions

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        sessions = self.get_all_sessions()
        for s in sessions:
            if str(s["id"]) == str(session_id):
                return s
        return None

    def update_session_title(self, session_id: str, title: str) -> bool:
        # FastAPI에 PATCH 엔드포인트가 없으므로, 추후 필요시 구현
        return False

    def delete_session(self, session_id: str) -> bool:
        """세션 삭제 (오프라인 대응 포함)"""
        # session_id를 문자열로 변환 (백엔드에서 int로 올 수 있음)
        session_id_str = str(session_id)
        
        # 오프라인 세션인 경우
        if session_id_str.startswith("offline_"):
            return self._offline_cache.pop(session_id_str, None) is not None
        
        if not self._is_backend_available():
            # 백엔드 세션이지만 오프라인인 경우, 캐시에서만 제거
            self._offline_cache.pop(session_id_str, None)
            return True
        
        try:
            resp = requests.delete(f"{self.backend_url}/chat/sessions/{session_id}", timeout=10)
            return resp.status_code == 200
        except Exception as e:
            self._handle_api_error("세션 삭제", e)
            return False

    def save_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """메시지 저장 (오프라인 대응 포함)"""
        import streamlit as st
        
        # session_id를 문자열로 변환 (백엔드에서 int로 올 수 있음)
        session_id_str = str(session_id)
        
        # 오프라인 세션인 경우
        if session_id_str.startswith("offline_"):
            if session_id_str in self._offline_cache:
                self._offline_cache[session_id_str]["messages"].append(message)
                return True
            return False
        
        if not self._is_backend_available():
            # 백엔드 세션이지만 오프라인인 경우, 임시 저장
            if session_id_str not in self._offline_cache:
                self._offline_cache[session_id_str] = {"messages": []}
            self._offline_cache[session_id_str]["messages"].append(message)
            st.info("📱 오프라인 모드: 메시지가 임시 저장되었습니다.")
            return True
        
        try:
            payload = {
                "session_id": int(session_id),
                "role": message["role"],
                "content": message["content"]
            }
            resp = requests.post(f"{self.backend_url}/chat/messages", json=payload, timeout=15)
            return resp.status_code == 200
        except Exception as e:
            self._handle_api_error("메시지 저장", e)
            return False

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """메시지 목록 조회 (오프라인 캐시 포함)"""
        # session_id를 문자열로 변환 (백엔드에서 int로 올 수 있음)
        session_id_str = str(session_id)
        
        # 오프라인 세션인 경우
        if session_id_str.startswith("offline_"):
            return self._offline_cache.get(session_id_str, {}).get("messages", [])
        
        # 오프라인 캐시에 메시지가 있는 경우 (백엔드 세션이지만 임시 저장된 메시지)
        cached_messages = self._offline_cache.get(session_id_str, {}).get("messages", [])
        
        if not self._is_backend_available():
            return cached_messages
        
        try:
            resp = requests.get(f"{self.backend_url}/chat/messages", 
                              params={"session_id": session_id}, timeout=10)
            if resp.status_code == 200:
                backend_messages = resp.json()
                # 백엔드 메시지와 캐시된 메시지 합치기 (중복 제거 필요시)
                return backend_messages + cached_messages
            else:
                return cached_messages
        except Exception as e:
            self._handle_api_error("메시지 조회", e)
            return cached_messages

    def delete_message(self, message_id: int) -> bool:
        resp = requests.delete(f"{self.backend_url}/chat/messages/{message_id}")
        return resp.status_code == 200

    def search_sessions(self, query: str) -> List[Dict[str, Any]]:
        """세션 검색 (개선된 로직)"""
        sessions = self.get_all_sessions()
        query_lower = query.lower()
        matching_sessions = []
        
        for session in sessions:
            # 제목에서 검색
            if query_lower in session.get('title', '').lower():
                matching_sessions.append(session)
                continue
            
            # 첫 번째 메시지에서 검색 (있는 경우)
            first_message = session.get('first_message', '')
            if first_message and query_lower in first_message.lower():
                matching_sessions.append(session)
        
        matching_sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return matching_sessions

chat_storage = ChatStorage()
