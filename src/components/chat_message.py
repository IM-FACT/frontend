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
    - 답변 본문만 메시지 컨테이너에 렌더링
    - 출처는 추출해서 반환 (별도 렌더링용)
    """
    content = message["content"]
    
    # time 또는 created_at 필드에서 시간 추출 (안전 처리)
    time_display = message.get("time") or message.get("created_at", "")
    if "T" in str(time_display):  # ISO 형식이면 시간만 추출
        time_display = time_display.split("T")[1][:5] if "T" in time_display else time_display

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
    
    # 출처는 세션 상태에 저장해서 별도 렌더링
    if sources:
        if 'current_sources' not in st.session_state:
            st.session_state.current_sources = []
        st.session_state.current_sources = sources
    else:
        # 출처가 없으면 현재 출처 목록 초기화
        st.session_state.current_sources = []


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
    Perplexity 스타일의 출처 섹션을 렌더링합니다.
    세션 상태에 저장된 출처들을 메시지 밖 별도 영역에 표시
    """
    if hasattr(st.session_state, 'current_sources') and st.session_state.current_sources:
        sources = st.session_state.current_sources
        
        # Perplexity 스타일 출처 섹션
        st.markdown("""
        <div class="perplexity-sources-section">
            <div class="sources-header">
                <span class="sources-title">📚 출처</span>
                <span class="sources-count">{} 개</span>
            </div>
        </div>
        """.format(len(sources)), unsafe_allow_html=True)
        
        # 출처 버튼들을 한 줄로 배치
        cols = st.columns(min(len(sources), 4))  # 최대 4개 컬럼
        for i, source in enumerate(sources):
            with cols[i % 4]:
                # 도메인 추출
                import re
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', source['url'])
                domain = domain_match.group(1) if domain_match else "링크"
                
                st.link_button(
                    f"🔗 {domain}",
                    source['url'],
                    use_container_width=True
                )


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
