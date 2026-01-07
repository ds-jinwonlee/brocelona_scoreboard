# Brocelona League Dashboard

브로셀로나 리그의 경기 결과와 승점을 시각화하는 대시보드입니다.

## 프로젝트 구조

```
brocelona_score/
├── src/                      # 소스 코드
│   ├── __init__.py
│   ├── app.py               # Streamlit 메인 애플리케이션
│   └── utils/               # 유틸리티 모듈
│       ├── __init__.py
│       └── data_loader.py   # 데이터 로딩 및 처리
├── data/                    # 데이터 파일
│   ├── match_result_sample.tsv
│   └── attendance_sample.tsv
├── docs/                    # 문서
│   └── implementation_plan.md
├── requirements.txt         # Python 의존성
├── run.sh                   # 실행 스크립트
└── README.md               # 프로젝트 문서
```

## 설치

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## 실행

### 방법 1: 실행 스크립트 사용
```bash
chmod +x run.sh
./run.sh
```

### 방법 2: Streamlit 직접 실행
```bash
streamlit run src/app.py --server.port 8501
```

### 방법 3: Conda 환경에서 실행
```bash
conda run -n brocelona_scoreboard streamlit run src/app.py --server.port 8501
```

## 기능

- **🏆 종합 순위**: 팀별 승점, 득실차 등 순위표
- **🏃 개인 기록**: 득점왕, 출석왕, 가성비 스트라이커, 승점 요정
- **📈 트렌드 분석**: 주차별 누적 승점 그래프

## 데이터 업데이트

새로운 경기 결과나 출석 데이터를 업데이트하려면 `data/` 폴더의 TSV 파일을 수정하세요:
- `data/match_result_sample.tsv`: 경기 결과
- `data/attendance_sample.tsv`: 출석 데이터
