def load_css():
    """
    CSS 파일들을 로드하고 Streamlit에 적용하는 함수
    - CSS 파일들을 캐시하여 성능 향상
    - 에러 처리 강화
    - CSS 최적화 (공백 제거, 주석 제거)
    - 개발/운영 환경 분리
    """
    import streamlit as st
    import os
    import re
    from functools import lru_cache
    
    @lru_cache(maxsize=1)
    def get_css_content():
        styles_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles")
        
        # CSS 파일 로딩 순서 정의 (의존성 순서 중요)
        css_files = [
            "variables.css",  # 1. 변수 정의 (최우선)
            "base.css",       # 2. 기본 스타일 및 Streamlit 오버라이드
            "layout.css",     # 3. 레이아웃 (사이드바, 컨테이너)
            "components.css", # 4. 컴포넌트 (채팅, 버튼 등)
            "utilities.css"   # 5. 유틸리티 클래스 (최종)
        ]
        
        combined_css = []
        loaded_files = []
        
        for css_file in css_files:
            file_path = os.path.join(styles_dir, css_file)
            try:
                if not os.path.exists(file_path):
                    st.warning(f"⚠️ CSS 파일을 찾을 수 없습니다: {css_file}")
                    continue
                
                with open(file_path, "r", encoding="utf-8") as f:
                    css_content = f.read()
                    
                    # CSS 최적화 (운영 환경에서만)
                    if not st.session_state.get('debug_mode', False):
                        # 1. 주석 제거 (/* ... */ 형태)
                        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
                        # 2. 연속된 공백을 하나로 압축
                        css_content = re.sub(r'\s+', ' ', css_content)
                        # 3. 선택자와 속성 사이의 불필요한 공백 제거
                        css_content = re.sub(r'}\s*{', '}{', css_content)
                        # 4. 마지막 세미콜론 제거
                        css_content = re.sub(r';\s*}', '}', css_content)
                        # 5. 줄바꿈 제거
                        css_content = css_content.strip()
                    
                    combined_css.append(f"/* {css_file} */\n{css_content}")
                    loaded_files.append(css_file)
                    
            except FileNotFoundError:
                st.error(f"❌ CSS 파일을 찾을 수 없습니다: {css_file}")
            except PermissionError:
                st.error(f"🚫 CSS 파일 접근 권한이 없습니다: {css_file}")
            except UnicodeDecodeError:
                st.error(f"📝 CSS 파일 인코딩 오류: {css_file} (UTF-8로 저장해주세요)")
            except Exception as e:
                st.error(f"🔧 CSS 파일 로딩 중 예상치 못한 오류: {css_file} - {str(e)}")
        
        # 로딩 성공 로그 (디버그 모드에서만)
        if st.session_state.get('debug_mode', False):
            st.success(f"✅ CSS 파일 로딩 완료: {', '.join(loaded_files)}")
        
        return "\n".join(combined_css)
    
    try:
        css_content = get_css_content()
        if css_content:
            # CSS 변수 주입 (동적 테마 지원)
            css_content = inject_dynamic_variables(css_content)
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        else:
            st.warning("⚠️ 로드된 CSS 내용이 없습니다.")
    except Exception as e:
        st.error(f"🚨 CSS 적용 중 치명적 오류 발생: {str(e)}")
        # 기본 스타일이라도 적용 (fallback)
        fallback_css = """
        .main .block-container {
            max-width: 800px !important;
            margin: 0 auto !important;
        }
        """
        st.markdown(f"<style>{fallback_css}</style>", unsafe_allow_html=True)

def inject_dynamic_variables(css_content: str) -> str:
    """
    CSS에 동적 변수를 주입합니다.
    사용자 설정이나 테마에 따라 CSS 변수를 동적으로 변경 가능
    """
    import streamlit as st
    
    # 사용자 설정에서 테마 가져오기 (기본값: dark)
    theme = st.session_state.get('user_theme', 'dark')
    
    # 테마별 변수 오버라이드
    if theme == 'light':
        theme_variables = """
        :root {
            --bg-primary: #ffffff !important;
            --bg-secondary: rgba(0, 0, 0, 0.02) !important;
            --text-primary: #1a1a1a !important;
            --text-secondary: rgba(26, 26, 26, 0.7) !important;
            --border-color: rgba(0, 0, 0, 0.08) !important;
        }
        """
        css_content = theme_variables + css_content
    
    return css_content
