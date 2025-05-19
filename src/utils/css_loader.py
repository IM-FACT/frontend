def load_css():
    """
    CSS 파일들을 로드하고 Streamlit에 적용하는 함수
    """
    import streamlit as st
    import os
    
    # CSS 파일 경로
    css_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles")
    
    # 메인 CSS 파일 내용 가져오기
    with open(os.path.join(css_dir, "main.css"), "r", encoding="utf-8") as f:
        css = f.read()
    
    # Streamlit에 CSS 적용
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
