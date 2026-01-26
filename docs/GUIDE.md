# ⚽ Brocelona League Dashboard 가이드

본 가이드는 구글 시트를 연동하고 서비스를 배포하는 가장 쉽고 빠른 방법을 설명합니다.

## 1. 데이터 소스 (Google Sheets) 설정

복잡한 API 설정 없이, 공유 설정만으로 연동됩니다.

1.  **구글 시트 생성**: 본인의 구글 드라이브에 시트를 만듭니다.
2.  **시트 이름 변경**: 하단 탭 이름을 각각 `match_result`와 `attendance`로 변경합니다. (매우 중요!)
3.  **데이터 입력**: 형식에 맞춰 데이터를 입력합니다.
4.  **권한 설정**: 우측 상단 **[공유]** 클릭 -> 일반 액세스를 **"링크가 있는 모든 사용자"** (뷰어)로 변경합니다.
5.  **URL 복사**: 브라우저 주소창의 URL(`.../edit#gid=0` 포함 전체)을 복사합니다.

## 2. Streamlit Cloud 배포 (3분 소요)

1.  **GitHub 푸시**: 코드를 본인의 저장소에 푸시합니다.
2.  **Streamlit Cloud 접속**: [share.streamlit.io](https://share.streamlit.io/)에 접속하여 로그인합니다.
3.  **New App 생성**: 본인의 GitHub 저장소를 연결합니다. (Main file: `src/app.py`)
4.  **Secrets 설정** (가장 중요):
    *   배포 설정 창의 **[Advanced settings...]**를 누릅니다.
    *   **Secrets** 칸에 아래 내용을 넣습니다 (복사한 URL 사용):
        ```toml
        [google_sheets]
        spreadsheet_url = "복사한_구글시트_URL"
        ```
5.  **Environment variables 설정**:
    *   같은 창의 **Environment variables** 칸에 아래 내용을 넣습니다:
        ```
        USE_GOOGLE_SHEETS=true
        ```
6.  **Deploy!**: 버튼을 누르면 배포가 시작됩니다.

## 3. 매주 데이터 업데이트

1.  **구글 시트**에 새로운 라운드 결과를 추가합니다.
2.  대시보드 앱으로 돌아와 **새로고침(F5)** 또는 우측 상단 메뉴의 **Rerun**을 누르면 즉시 반영됩니다.

---

**팁**: 로컬에서 테스트할 때는 터미널에서 `export USE_GOOGLE_SHEETS=false`로 설정하면 `data/` 폴더의 TSV 파일을 읽어옵니다.
