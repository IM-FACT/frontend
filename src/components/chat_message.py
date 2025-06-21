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

    # 기존에 저장된 출처가 있으면 사용, 없으면 새로 추출
    if "sources" in message and message["sources"]:
        sources = message["sources"]
        body = content  # 이미 처리된 본문
    else:
        # 답변에서 출처 URL 자동 추출 (다양한 패턴 지원)
        sources = []
        
        # 1. 번호가 있는 URL: "1. https://example.com" 
        numbered_url_pattern = r"^(\d+)\.\s*(https?://\S+)"
        
        # 2. 일반 URL: "https://example.com" 또는 "출처: https://example.com"
        general_url_pattern = r"(https?://[^\s]+)"
        
        # 3. 도메인만 있는 경우: "news.kbs.co.kr" -> "https://news.kbs.co.kr"로 변환
        domain_pattern = r"(?:^|\s)([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})(?:\s|$)"
        
        lines = content.strip().split("\n")
        body_lines = []
        
        for line in lines:
            line_processed = False
            
            # 1. 번호가 있는 URL 패턴 확인
            m = re.match(numbered_url_pattern, line.strip())
            if m:
                num, url = m.groups()
                sources.append({"num": num, "url": url})
                line_processed = True
            
            # 2. 일반 URL 패턴에서 URL 추출
            elif not line_processed:
                urls = re.findall(general_url_pattern, line)
                for url in urls:
                    sources.append({"num": str(len(sources) + 1), "url": url})
            
            # 3. 도메인만 있는 경우 (news.kbs.co.kr 같은)
            if not line_processed and not re.search(general_url_pattern, line):
                domains = re.findall(domain_pattern, line)
                for domain in domains:
                    # 일반적인 도메인이고 URL이 아닌 경우에만 처리
                    if "." in domain and not domain.startswith("http") and len(domain.split(".")) >= 2:
                        url = f"https://{domain}"
                        sources.append({"num": str(len(sources) + 1), "url": url})
                        line_processed = True
            
            # URL/도메인이 포함된 줄이 아니면 본문에 추가
            if not line_processed:
                body_lines.append(line)
        
        body = "\n".join(body_lines).strip()
        
        # 메시지에 출처 저장 (다음번 렌더링을 위해)
        message["sources"] = sources

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
        # 도메인 추출 및 정리
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', source['url'])
        if domain_match:
            domain = domain_match.group(1)
            
            # 일반적인 도메인 정리
            if domain.startswith('m.'):
                domain = domain[2:]  # 모바일 버전 제거
            
            # 너무 긴 도메인 줄이기
            if len(domain) > 25:
                parts = domain.split('.')
                if len(parts) > 2:
                    domain = f"{parts[0][:8]}...{parts[-1]}"
                else:
                    domain = domain[:22] + "..."
        else:
            domain = "외부 링크"
        
        # 출처 버튼 HTML 생성
        source_buttons_html += f'<a href="{source["url"]}" target="_blank" class="source-link-button" title="{source["url"]}">{domain}</a>'
    
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
