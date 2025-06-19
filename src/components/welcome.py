"""
환영 메시지 및 로고 컴포넌트
앱의 브랜딩 요소와 환영 메시지를 표시합니다.
"""
import streamlit as st
from typing import Optional, Dict


def render_logo(
    main_text: str = "IM.",
    highlight_text: str = "FACT",
    badge_text: Optional[str] = "eco",
    custom_style: Optional[Dict[str, str]] = None
) -> None:
    """
    로고를 렌더링합니다.
    
    Args:
        main_text: 메인 텍스트
        highlight_text: 하이라이트 텍스트
        badge_text: 뱃지 텍스트 (None이면 표시하지 않음)
        custom_style: 커스텀 스타일 딕셔너리
    """
    badge_html = f'<span class="logo-badge">{badge_text}</span>' if badge_text else ""
    
    logo_html = f"""
    <div class="logo-container">
        <div class="logo-text">{main_text}<span class="logo-highlight">{highlight_text}</span>{badge_html}</div>
    </div>
    """
    
    st.markdown(logo_html, unsafe_allow_html=True)


def render_welcome_message(message: str) -> None:
    """
    환영 메시지를 렌더링합니다.
    
    Args:
        message: 환영 메시지 텍스트
    """
    welcome_html = f"""
    <div class="welcome-text">
        {message}
    </div>
    """
    
    st.markdown(welcome_html, unsafe_allow_html=True)


def render_home_welcome() -> None:
    """
    홈 탭의 기본 환영 화면을 렌더링합니다.
    """
    render_logo()
    render_welcome_message(
        "환경, 기후변화, 지속가능성에 관한 신뢰할 수 있는 정보를 제공합니다. "
        "IM.FACT는 IPCC, UN환경계획, 기상청 등의 공식 자료를 기반으로 과학적이고 균형 잡힌 답변을 제공합니다."
    )


def render_tab_header(
    title: str,
    highlight_word: Optional[str] = None,
    description: Optional[str] = None
) -> None:
    """
    각 탭의 헤더를 렌더링합니다.
    
    Args:
        title: 탭 제목
        highlight_word: 하이라이트할 단어
        description: 탭 설명
    """
    if highlight_word and highlight_word in title:
        # 하이라이트 단어를 분리
        parts = title.split(highlight_word, 1)
        title_html = f'{parts[0]}<span class="logo-highlight">{highlight_word}</span>{parts[1] if len(parts) > 1 else ""}'
    else:
        title_html = title
    
    header_html = f"""
    <div class="logo-container">
        <div class="logo-text">{title_html}</div>
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)
    
    if description:
        render_welcome_message(description)


# 각 탭별 헤더 정보
TAB_HEADERS = {
    "history": {
        "title": "대화 기록",
        "highlight": "기록",
        "description": "이전 대화 기록을 확인하고 계속할 수 있습니다."
    }
}


def render_tab_welcome(tab_id: str) -> None:
    """
    특정 탭의 환영 화면을 렌더링합니다.
    
    Args:
        tab_id: 탭 ID
    """
    if tab_id == "home":
        render_home_welcome()
    elif tab_id in TAB_HEADERS:
        header_info = TAB_HEADERS[tab_id]
        render_tab_header(
            title=header_info["title"],
            highlight_word=header_info.get("highlight"),
            description=header_info.get("description")
        )
