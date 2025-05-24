"""
빠른 질문 버튼 컴포넌트
자주 묻는 질문들을 빠르게 선택할 수 있는 버튼 그룹을 제공합니다.
"""
import streamlit as st
from typing import List, Dict, Callable, Optional


# 기본 빠른 질문 버튼 정의
DEFAULT_QUICK_BUTTONS = [
    {
        "icon": "🌡️",
        "label": "기후변화",
        "query": "기후변화가 한국에 미치는 영향은?",
        "key": "btn_climate_impact"
    },
    {
        "icon": "♻️",
        "label": "탄소중립",
        "query": "탄소중립이란 무엇인가요?",
        "key": "btn_carbon_neutral"
    },
    {
        "icon": "🌐",
        "label": "IPCC",
        "query": "IPCC란 무엇인가요?",
        "key": "btn_ipcc"
    },
    {
        "icon": "📊",
        "label": "온실가스",
        "query": "한국의 온실가스 배출 현황은?",
        "key": "btn_emissions"
    },
    {
        "icon": "💪",
        "label": "실천방법",
        "query": "기후변화 대응 방법은?",
        "key": "btn_personal"
    }
]


def render_quick_buttons(
    buttons: Optional[List[Dict[str, str]]] = None,
    on_click: Optional[Callable[[str], None]] = None,
    columns_widths: Optional[List[float]] = None
) -> None:
    """
    빠른 질문 버튼들을 렌더링합니다.
    
    Args:
        buttons: 버튼 정의 리스트. None이면 DEFAULT_QUICK_BUTTONS 사용
        on_click: 버튼 클릭 시 실행할 콜백 함수. 쿼리 문자열을 인자로 받음
        columns_widths: 각 컬럼의 너비 비율. None이면 자동 계산
    """
    if buttons is None:
        buttons = DEFAULT_QUICK_BUTTONS
    
    # 버튼 컨테이너
    st.markdown('<div class="imfact-button-container">', unsafe_allow_html=True)
    
    # 컬럼 너비 설정
    if columns_widths is None:
        # 기본 너비 설정 (버튼 텍스트 길이에 따라 조정)
        columns_widths = [0.9, 1, 0.8, 1, 1.1]
    
    cols = st.columns(columns_widths)
    
    # 버튼 렌더링
    for i, button_def in enumerate(buttons):
        if i < len(cols):
            with cols[i]:
                button_text = f"{button_def['icon']} {button_def['label']}"
                if st.button(
                    button_text, 
                    key=button_def["key"], 
                    use_container_width=True
                ):
                    if on_click:
                        on_click(button_def["query"])
                    else:
                        # 기본 동작: 세션 상태에 질문 저장
                        st.session_state.chat_input = button_def["query"]
                        if hasattr(st.session_state, 'handle_user_input'):
                            st.session_state.handle_user_input()
    
    st.markdown('</div>', unsafe_allow_html=True)


def create_custom_quick_button(
    icon: str,
    label: str,
    query: str,
    key: Optional[str] = None
) -> Dict[str, str]:
    """
    커스텀 빠른 질문 버튼을 생성합니다.
    
    Args:
        icon: 버튼 아이콘 (이모지)
        label: 버튼 라벨
        query: 클릭 시 입력될 질문
        key: 버튼의 고유 키 (선택사항)
        
    Returns:
        버튼 정의 딕셔너리
    """
    if key is None:
        # 라벨 기반으로 키 자동 생성
        key = f"btn_{label.lower().replace(' ', '_')}"
    
    return {
        "icon": icon,
        "label": label,
        "query": query,
        "key": key
    }


def get_category_buttons(category: str) -> List[Dict[str, str]]:
    """
    특정 카테고리의 빠른 질문 버튼들을 반환합니다.
    
    Args:
        category: 카테고리 이름 (예: 'climate', 'carbon', 'action')
        
    Returns:
        해당 카테고리의 버튼 리스트
    """
    categories = {
        "climate": [
            create_custom_quick_button("🌡️", "기후변화", "기후변화가 한국에 미치는 영향은?"),
            create_custom_quick_button("🌊", "해수면상승", "해수면 상승의 현재 상황과 전망은?"),
            create_custom_quick_button("🌪️", "극한기상", "극한 기상 현상이 증가하는 이유는?"),
        ],
        "carbon": [
            create_custom_quick_button("♻️", "탄소중립", "탄소중립이란 무엇인가요?"),
            create_custom_quick_button("🏭", "탄소배출", "주요 탄소 배출원은 무엇인가요?"),
            create_custom_quick_button("🌳", "탄소흡수", "탄소 흡수원의 역할은?"),
        ],
        "action": [
            create_custom_quick_button("💪", "개인실천", "개인이 할 수 있는 기후 행동은?"),
            create_custom_quick_button("🏢", "기업역할", "기업의 탄소중립 실천 방법은?"),
            create_custom_quick_button("🏛️", "정책지원", "정부의 기후변화 대응 정책은?"),
        ]
    }
    
    return categories.get(category, DEFAULT_QUICK_BUTTONS)
