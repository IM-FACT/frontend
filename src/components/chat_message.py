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
            - time 또는 created_at: 메시지 시간
    """
    # time 또는 created_at 필드에서 시간 추출 (안전 처리)
    time_display = message.get("time") or message.get("created_at", "")
    if "T" in str(time_display):  # ISO 형식이면 시간만 추출
        time_display = time_display.split("T")[1][:5] if "T" in time_display else time_display
    
    st.markdown(f"""
    <div class="imfact-chat-message user">
        <div class="message-header">
            <div class="avatar user-avatar">U</div>
            <span class="name-title">You</span>
            <span class="time">{time_display}</span>
        </div>
        <div class="message-content">
            {message["content"]}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_assistant_message(message: Dict[str, any]) -> None:
    """
    어시스턴트 메시지를 렌더링합니다.
    메시지와 출처를 함께 표시 (Perplexity 스타일)
    """
    content = message["content"]
    
    # time 또는 created_at 필드에서 시간 추출 (안전 처리)
    time_display = message.get("time") or message.get("created_at", "")
    if "T" in str(time_display):  # ISO 형식이면 시간만 추출
        time_display = time_display.split("T")[1][:5] if "T" in time_display else time_display

    # 기존에 저장된 출처가 있으면 사용, 없으면 빈 리스트로 초기화
    sources = message.get("sources") or []
    body = content

    # 특수 태그 변환 (인용문, 주요 팩트 등)
    body = body.replace("<citation>", '<div class="imfact-citation">').replace("</citation>", '</div>')
    body = body.replace("<key-fact>", '<span class="key-fact">').replace("</key-fact>", '</span>')
    body = body.replace("<data-visualization>", '<div class="data-visualization">').replace("</data-visualization>", '</div>')

    # 줄바꿈을 HTML로 변환
    body_html = body.replace('\n', '<br>')

    # 메시지 본문 렌더링
    st.markdown(f"""
    <div class="imfact-chat-message assistant">
        <div class="message-header">
            <div class="avatar assistant-avatar">🌍</div>
            <span class="name-title">IM.FACT</span>
            <span class="time">{time_display}</span>
        </div>
        <div class="message-content">
            {body_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 출처가 있으면 메시지 바로 아래에 표시 (Perplexity 스타일)
    if sources:
        render_message_sources(sources)


def render_message_sources(sources: List[Dict[str, str]]) -> None:
    """
    특정 메시지의 출처를 렌더링합니다. (메시지별 출처)
    
    Args:
        sources: 출처 정보 리스트
    """
    if not sources:
        return
    
    # 출처 버튼들을 그리드 없이 직접 렌더링
    source_buttons_html = '<div class="sources-grid">'
    for i, source in enumerate(sources):
        # 이제 도메인 대신 title을 사용
        title = source.get("title", "출처 보기")
        if not title or not title.strip():
            title = "제목 없음"
        
        # 너무 긴 제목 줄이기
        if len(title) > 35:
            title = title[:32] + "..."
            
        # 출처 버튼 HTML 생성
        source_buttons_html += f'<a href="{source["url"]}" target="_blank" class="source-link-button" title="{source.get("title", "원본 링크")}\nURL: {source["url"]}">{title}</a>'
    
    source_buttons_html += '</div>'
    
    # 모든 출처 버튼을 한 번에 렌더링 (컨테이너 없이)
    st.markdown(source_buttons_html, unsafe_allow_html=True)


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


def render_sources_section() -> None:
    """
    전역 출처 섹션 - 더 이상 사용하지 않음
    메시지별 출처로 대체됨
    """
    pass  # 빈 함수로 유지 (기존 호출 코드와의 호환성을 위해)


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
