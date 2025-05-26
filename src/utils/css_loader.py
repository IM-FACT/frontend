def load_css():
    """
    CSS 파일들을 로드하고 Streamlit에 적용하는 함수
    - CSS 파일들을 캐시하여 성능 향상
    - 에러 처리 강화
    - CSS 최적화 (공백 제거, 주석 제거)
    """
    import streamlit as st
    import os
    import re
    from functools import lru_cache
    
    @lru_cache(maxsize=1)
    def get_css_content():
        styles_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles")
        
        # CSS 파일 로딩 순서 정의
        css_files = [
            "variables.css",  # 변수 정의
            "base.css",       # 기본 스타일
            "layout.css",     # 레이아웃
            "components.css", # 컴포넌트
            "utilities.css"   # 유틸리티
        ]
        
        combined_css = []
        for css_file in css_files:
            file_path = os.path.join(styles_dir, css_file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    css_content = f.read()
                    
                    # CSS 최적화
                    # 1. 주석 제거
                    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
                    # 2. 불필요한 공백 제거
                    css_content = re.sub(r'\s+', ' ', css_content)
                    # 3. 선택자와 속성 사이의 공백 정리
                    css_content = re.sub(r'}\s*{', '}{', css_content)
                    # 4. 마지막 세미콜론 제거
                    css_content = re.sub(r';\s*}', '}', css_content)
                    
                    combined_css.append(css_content)
            except FileNotFoundError:
                st.error(f"CSS 파일을 찾을 수 없습니다: {css_file}")
            except Exception as e:
                st.error(f"CSS 파일 로딩 중 오류 발생: {css_file} - {str(e)}")
        
        return "\n".join(combined_css)
    
    try:
        css_content = get_css_content()
        if css_content:
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"CSS 적용 중 오류 발생: {str(e)}")
