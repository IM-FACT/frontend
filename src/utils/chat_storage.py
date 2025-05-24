"""
채팅 기록 저장 및 관리 유틸리티
JSON 파일로 대화 기록을 영구 저장하고 관리합니다.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
from pathlib import Path


class ChatStorage:
    """채팅 기록을 파일 시스템에 저장하고 관리하는 클래스"""
    
    def __init__(self, storage_path: str = "chat_history"):
        """
        Args:
            storage_path: 채팅 기록을 저장할 디렉토리 경로
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.sessions_file = self.storage_path / "sessions.json"
        self.chats_dir = self.storage_path / "chats"
        self.chats_dir.mkdir(exist_ok=True)
        
        # 세션 목록 초기화
        self._initialize_sessions()
    
    def _initialize_sessions(self) -> None:
        """세션 목록 파일 초기화"""
        if not self.sessions_file.exists():
            self._save_sessions({})
    
    def _load_sessions(self) -> Dict[str, Dict[str, Any]]:
        """세션 목록 로드"""
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_sessions(self, sessions: Dict[str, Dict[str, Any]]) -> None:
        """세션 목록 저장"""
        with open(self.sessions_file, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
    
    def create_session(self, title: Optional[str] = None) -> str:
        """
        새로운 채팅 세션 생성
        
        Args:
            title: 세션 제목 (없으면 자동 생성)
            
        Returns:
            생성된 세션 ID
        """
        session_id = str(uuid.uuid4())
        sessions = self._load_sessions()
        
        now = datetime.now()
        sessions[session_id] = {
            "id": session_id,
            "title": title or f"대화 {now.strftime('%Y-%m-%d %H:%M')}",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "message_count": 0,
            "first_message": None
        }
        
        self._save_sessions(sessions)
        
        # 빈 채팅 파일 생성
        chat_file = self.chats_dir / f"{session_id}.json"
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        
        return session_id
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        모든 세션 목록 반환 (최근 수정 순으로 정렬)
        
        Returns:
            세션 정보 리스트
        """
        sessions = self._load_sessions()
        sessions_list = list(sessions.values())
        
        # 최근 수정 순으로 정렬
        sessions_list.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return sessions_list
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 세션 정보 반환
        
        Args:
            session_id: 세션 ID
            
        Returns:
            세션 정보 또는 None
        """
        sessions = self._load_sessions()
        return sessions.get(session_id)
    
    def update_session_title(self, session_id: str, title: str) -> bool:
        """
        세션 제목 업데이트
        
        Args:
            session_id: 세션 ID
            title: 새 제목
            
        Returns:
            성공 여부
        """
        sessions = self._load_sessions()
        if session_id in sessions:
            sessions[session_id]['title'] = title
            sessions[session_id]['updated_at'] = datetime.now().isoformat()
            self._save_sessions(sessions)
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        세션 삭제
        
        Args:
            session_id: 세션 ID
            
        Returns:
            성공 여부
        """
        sessions = self._load_sessions()
        if session_id in sessions:
            # 세션 목록에서 제거
            del sessions[session_id]
            self._save_sessions(sessions)
            
            # 채팅 파일 삭제
            chat_file = self.chats_dir / f"{session_id}.json"
            if chat_file.exists():
                chat_file.unlink()
            
            return True
        return False
    
    def save_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """
        메시지 저장
        
        Args:
            session_id: 세션 ID
            message: 메시지 정보 (role, content, time, sources 등)
            
        Returns:
            성공 여부
        """
        chat_file = self.chats_dir / f"{session_id}.json"
        
        # 기존 메시지 로드
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messages = []
        
        # 메시지 추가
        message['timestamp'] = datetime.now().isoformat()
        messages.append(message)
        
        # 저장
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        
        # 세션 정보 업데이트
        sessions = self._load_sessions()
        if session_id in sessions:
            sessions[session_id]['updated_at'] = datetime.now().isoformat()
            sessions[session_id]['message_count'] = len(messages)
            
            # 첫 번째 사용자 메시지를 세션 설명으로 사용
            if not sessions[session_id]['first_message'] and message['role'] == 'user':
                sessions[session_id]['first_message'] = message['content'][:100] + '...' if len(message['content']) > 100 else message['content']
            
            self._save_sessions(sessions)
        
        return True
    
    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        세션의 모든 메시지 반환
        
        Args:
            session_id: 세션 ID
            
        Returns:
            메시지 리스트
        """
        chat_file = self.chats_dir / f"{session_id}.json"
        
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def search_sessions(self, query: str) -> List[Dict[str, Any]]:
        """
        세션 제목 또는 첫 메시지로 검색
        
        Args:
            query: 검색어
            
        Returns:
            매칭되는 세션 리스트
        """
        sessions = self._load_sessions()
        query_lower = query.lower()
        
        matching_sessions = []
        for session in sessions.values():
            # 제목에서 검색
            if query_lower in session['title'].lower():
                matching_sessions.append(session)
                continue
            
            # 첫 메시지에서 검색
            if session['first_message'] and query_lower in session['first_message'].lower():
                matching_sessions.append(session)
        
        # 최근 수정 순으로 정렬
        matching_sessions.sort(key=lambda x: x['updated_at'], reverse=True)
        
        return matching_sessions
    



# 싱글톤 인스턴스
chat_storage = ChatStorage()
