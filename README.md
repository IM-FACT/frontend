# IM.FACT Frontend

IM.FACT의 프론트엔드 애플리케이션입니다. Streamlit을 사용하여 구현되었습니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
`.env` 파일을 생성하고 필요한 환경 변수를 설정합니다.

## 실행 방법

```bash
streamlit run app.py
```

## 주요 기능

- 환경 및 기후 관련 질문 입력
- 실시간 답변 생성
- 출처 정보 표시
- 사용자 친화적 인터페이스

## 기술 스택

- Streamlit
- Python
- FastAPI (백엔드 연동) 

## Streamlit 테마 적용

`.streamlit/config.toml` 파일을 통해 앱의 색상, 폰트 등 테마를 커스터마이징할 수 있습니다. 예시:

```
[theme]
primaryColor="#4fd1c5"
backgroundColor="#181c23"
secondaryBackgroundColor="#23272f"
textColor="#ffffff"
font="sans serif"
```

## UI/UX 개선 트렌드

- 컬럼(st.columns), 컨테이너(st.container), Expander(st.expander) 등 Streamlit 레이아웃 컴포넌트 적극 활용
- 트랜지션, 애니메이션, 마이크로인터랙션(hover, active 등)도 CSS로 추가 가능
- 반응형 레이아웃은 min/max-width, 컬럼 조합 등으로 최대한 대응 