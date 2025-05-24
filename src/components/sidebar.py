"""
사이드바 네비게이션 컴포넌트
앱의 주요 섹션으로 이동할 수 있는 사이드바 메뉴를 제공합니다.
"""
import streamlit as st
from typing import List, Dict, Optional


# 사이드바 메뉴 아이템 정의
SIDEBAR_ITEMS = [
    {"id": "home", "icon": "🌍", "title": "홈", "position": "top"},
    {"id": "history", "icon": "📝", "title": "대화 기록", "position": "top"},
    {"id": "data", "icon": "📊", "title": "지구 환경 데이터", "position": "top"},
    {"id": "sustainability", "icon": "🌐", "title": "지속가능성", "position": "top"},
    {"id": "carbon", "icon": "♻️", "title": "탄소중립", "position": "top"},
    {"id": "user", "icon": "👤", "title": "사용자 설정", "position": "bottom"}
]


def get_sidebar_html(current_tab: str) -> str:
    """
    사이드바 HTML을 생성합니다.
    
    Args:
        current_tab: 현재 활성화된 탭 ID
        
    Returns:
        사이드바 HTML 문자열
    """
    # 상단 아이템과 하단 아이템 분리
    top_items = [item for item in SIDEBAR_ITEMS if item["position"] == "top"]
    bottom_items = [item for item in SIDEBAR_ITEMS if item["position"] == "bottom"]
    
    # HTML 생성
    html = '<div class="sidebar">'
    
    # 상단 아이템들
    for item in top_items:
        is_active = current_tab == item["id"]
        active_class = "active" if is_active else ""
        html += f'<div class="sidebar-icon {active_class}">'
        html += f'<a href="?tab={item["id"]}" title="{item["title"]}" target="_self">{item["icon"]}</a>'
        html += '</div>'
    
    # 하단 아이템들 (사용자 설정)
    for item in bottom_items:
        is_active = current_tab == item["id"]
        active_class = "active" if is_active else ""
        html += f'<div class="sidebar-user {active_class}">'
        html += f'<a href="?tab={item["id"]}" title="{item["title"]}" target="_self">{item["icon"]}</a>'
        html += '</div>'
    
    html += '</div>'
    return html


def render_sidebar() -> None:
    """
    사이드바를 렌더링합니다.
    세션 상태에서 current_tab을 읽어 활성 상태를 표시합니다.
    """
    current_tab = st.session_state.get("current_tab", "home")
    # 디버깅을 위해 현재 탭 출력
    # st.write(f"Current tab: {current_tab}")
    sidebar_html = get_sidebar_html(current_tab)
    st.markdown(sidebar_html, unsafe_allow_html=True)


def handle_tab_change() -> Optional[str]:
    """
    URL 파라미터로부터 탭 변경을 감지하고 처리합니다.
    
    Returns:
        변경된 탭 ID 또는 None
    """
    if "tab" in st.query_params:
        tab_name = st.query_params["tab"]
        valid_tabs = [item["id"] for item in SIDEBAR_ITEMS]
        
        if tab_name in valid_tabs:
            return tab_name
    
    return None


def get_tab_info(tab_id: str) -> Optional[Dict[str, str]]:
    """
    탭 ID로 탭 정보를 조회합니다.
    
    Args:
        tab_id: 탭 ID
        
    Returns:
        탭 정보 딕셔너리 또는 None
    """
    for item in SIDEBAR_ITEMS:
        if item["id"] == tab_id:
            return item
    return None
