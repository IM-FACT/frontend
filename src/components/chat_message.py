"""
채팅 메시지 컴포넌트
사용자와 어시스턴트의 메시지를 표시하는 재사용 가능한 컴포넌트
"""
import streamlit as st
from typing import Dict, List, Optional
import re


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
    - 답변 본문은 마크다운으로 렌더링
    - 답변 내 번호 리스트(출처 URL 등)는 자동 추출하여 별도 영역에 시각적으로 구분
    - <div></div> 등 불필요한 태그 노출 방지
    - 인용문, 주요 팩트 등은 기존 스타일 유지
    """
    content = message["content"]

    # 답변에서 출처(번호+URL) 리스트 자동 추출
    # 예: 1. http...\n2. http...
    source_pattern = r"^(\d+)\.\s*(https?://\S+)"  # 번호. URL
    lines = content.strip().split("\n")
    sources = []
    body_lines = []
    for line in lines:
        m = re.match(source_pattern, line.strip())
        if m:
            sources.append(line.strip())
        else:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()

    # 특수 태그 변환 (인용문, 주요 팩트 등)
    body = body.replace("<citation>", '<div class="imfact-citation">').replace("</citation>", '</div>')
    body = body.replace("<key-fact>", '<span class="key-fact">').replace("</key-fact>", '</span>')
    body = body.replace("<data-visualization>", '<div class="data-visualization">').replace("</data-visualization>", '</div>')

    st.markdown(f"""
    <div class="imfact-chat-message assistant">
        <div class="message-header">
            <div class="avatar assistant-avatar">🌍</div>
            <span class="name-title">IM.FACT</span>
            <span class="time">{message["time"]}</span>
        </div>
        <div class="message-content">
    """, unsafe_allow_html=True)
    # 본문 마크다운 렌더링
    st.markdown(body, unsafe_allow_html=True)
    # 출처 리스트 별도 표시
    if sources:
        st.markdown('<div class="source-links"><span class="source-header">출처</span>', unsafe_allow_html=True)
        for src in sources:
            # 번호와 URL 분리
            m = re.match(source_pattern, src)
            if m:
                num, url = m.groups()
                st.markdown(f'<div class="source-link">{num}. <a href="{url}" target="_blank">{url}</a></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)


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
