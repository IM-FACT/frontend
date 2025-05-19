def load_css():
    """
    CSS 파일들을 로드하고 Streamlit에 적용하는 함수
    """
    import streamlit as st
    import os
    
    # 스타일 디렉토리 경로 생성
    styles_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles")
    
    # 각 CSS 파일을 직접 읽어서 하나의 CSS 문자열로 결합
    css_files = [
        "variables.css",
        "base.css",
        "layout.css",
        "components.css",
        "utilities.css"
    ]
    
    combined_css = ""
    for css_file in css_files:
        file_path = os.path.join(styles_dir, css_file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                combined_css += f.read() + "\n\n"
        except Exception as e:
            st.error(f"CSS 파일 로딩 오류: {css_file} - {str(e)}")
    
    # Streamlit에 CSS 적용
    if combined_css:
        st.markdown(f"<style>{combined_css}</style>", unsafe_allow_html=True)
