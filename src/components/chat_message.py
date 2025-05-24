"""
채팅 메시지 컴포넌트
사용자와 어시스턴트의 메시지를 표시하는 재사용 가능한 컴포넌트
"""
import streamlit as st
from typing import Dict, List, Optional


def render_user_message(message: Dict[str, str]) -> None:
    """
    사용자 메시지를 렌더링합니다.
    
    Args:
        message: 메시지 정보를 담은 딕셔너리
            - content: 메시지 내용
            - time: 메시지 시간
    """
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


def render_assistant_message(message: Dict[str, any]) -> None:
    """
    어시스턴트 메시지를 렌더링합니다.
    
    Args:
        message: 메시지 정보를 담은 딕셔너리
            - content: 메시지 내용
            - time: 메시지 시간
            - sources: 출처 정보 리스트 (선택사항)
    """
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


def render_typing_indicator() -> None:
    """
    타이핑 중 표시기를 렌더링합니다.
    """
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


def render_chat_message(message: Dict[str, any]) -> None:
    """
    메시지 타입에 따라 적절한 렌더링 함수를 호출합니다.
    
    Args:
        message: 메시지 정보를 담은 딕셔너리
            - role: 'user' 또는 'assistant'
            - content: 메시지 내용
            - time: 메시지 시간
            - sources: 출처 정보 리스트 (assistant 메시지인 경우, 선택사항)
    """
    if message["role"] == "user":
        render_user_message(message)
    elif message["role"] == "assistant":
        render_assistant_message(message)
