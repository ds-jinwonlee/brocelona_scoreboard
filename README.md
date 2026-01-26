# ⚽ Brocelona League Dashboard

브로셀로나 리그의 경기 결과와 승점 현황을 실시간으로 확인하는 대시보드입니다. 구글 시트와 연동되어 데이터 업데이트가 간편하며, Streamlit Cloud를 통해 서비스됩니다.

## 🚀 주요 기능

-   **🏆 종합 순위**: 승점, 경기수, 승/무/패, 득실차 자동 계산
-   **🏃 개인 기록**: 득점왕, 출석왕, 가성비 스트라이커, 승점 요정 랭킹
-   **📈 트렌드 분석**: 주차별 성적 추이 (막대+선 복합 그래프)
-   **📋 상세 결과**: 매치별 득점자 정보를 포함한 상세 스코어보드

## 🛠 기술 스택

-   **Frontend**: Streamlit
-   **Analysis**: Pandas
-   **Visualization**: Plotly
-   **Data Source**: Google Sheets (CSV Export API)

## 📦 설치 및 로컬 실행

1.  저장소 클론 및 패키지 설치:
    ```bash
    pip install -r requirements.txt
    ```

2.  로컬 실행:
    ```bash
    streamlit run src/app.py
    ```

## ☁️ Google Sheets 연동 및 배포

본 프로젝트는 구글 시트의 공개 URL을 통해 데이터를 동기화합니다. 상세한 설정 방법은 아래 가이드 문서를 참조하세요.

👉 **[배포 가이드 읽기 (docs/GUIDE.md)](docs/GUIDE.md)**

## 📁 프로젝트 구조

```text
src/
├── app.py           # Streamlit 메인 애플리케이션
└── utils/
    └── data_loader.py # Google Sheets 및 로컬 데이터 로더
data/                  # 로컬 테스트용 샘플 데이터 (TSV)
docs/
└── GUIDE.md           # 통합 배포 가이드
```

## 📝 데이터 포맷

구글 시트의 `match_result`와 `attendance` 시트 이름을 유지해야 하며, 헤더 형식이 로컬 샘플(`data/*.tsv`)과 동일해야 합니다.
