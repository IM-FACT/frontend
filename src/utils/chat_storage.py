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
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class ChatStorage:
    """
    백엔드 API를 통해 채팅 세션/메시지를 관리하는 클래스
    """
    def __init__(self):
        self.backend_url = BACKEND_URL

    def create_session(self, title: Optional[str] = None) -> str:
        payload = {"title": title or f"대화 {datetime.now().strftime('%Y-%m-%d %H:%M')}",}
        resp = requests.post(f"{self.backend_url}/chat/sessions", json=payload)
        if resp.status_code == 200:
            return resp.json()["id"]
        else:
            raise Exception(f"세션 생성 실패: {resp.text}")

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.backend_url}/chat/sessions")
        if resp.status_code == 200:
            sessions = resp.json()
            # 최신순 정렬 (created_at 기준)
            sessions.sort(key=lambda x: x['created_at'], reverse=True)
            return sessions
        else:
            return []

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
        resp = requests.delete(f"{self.backend_url}/chat/sessions/{session_id}")
        return resp.status_code == 200

    def save_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        payload = {
            "session_id": session_id,
            "role": message["role"],
            "content": message["content"]
        }
        resp = requests.post(f"{self.backend_url}/chat/messages", json=payload)
        return resp.status_code == 200

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        resp = requests.get(f"{self.backend_url}/chat/messages", params={"session_id": session_id})
        if resp.status_code == 200:
            return resp.json()
        else:
            return []

    def delete_message(self, message_id: int) -> bool:
        resp = requests.delete(f"{self.backend_url}/chat/messages/{message_id}")
        return resp.status_code == 200

    def search_sessions(self, query: str) -> List[Dict[str, Any]]:
        # 백엔드에 검색 API가 없으므로, 프론트에서 제목/첫 메시지로 필터링
        sessions = self.get_all_sessions()
        query_lower = query.lower()
        matching_sessions = []
        for session in sessions:
            if query_lower in session['title'].lower():
                matching_sessions.append(session)
        matching_sessions.sort(key=lambda x: x['created_at'], reverse=True)
        return matching_sessions

chat_storage = ChatStorage()
