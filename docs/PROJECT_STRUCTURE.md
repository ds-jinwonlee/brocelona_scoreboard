# 프로젝트 구조 정리 완료

## 📁 새로운 폴더 구조

```
brocelona_score/
├── src/                      # 소스 코드
│   ├── __init__.py          # 패키지 초기화
│   ├── app.py               # Streamlit 메인 애플리케이션
│   └── utils/               # 유틸리티 모듈
│       ├── __init__.py      # utils 패키지 초기화
│       └── data_loader.py   # 데이터 로딩 및 처리 함수
├── data/                    # 데이터 파일
│   ├── match_result_sample.tsv    # 경기 결과 데이터
│   └── attendance_sample.tsv       # 출석 데이터
├── docs/                    # 문서
│   └── implementation_plan.md     # 구현 계획서
├── requirements.txt         # Python 의존성 패키지 목록
├── run.sh                   # 실행 스크립트
└── README.md               # 프로젝트 설명서
```

## 🔧 주요 변경 사항

### 1. 코드 구조화
- **src/** 폴더에 모든 소스 코드 이동
- **src/utils/** 패키지로 유틸리티 함수 분리
- `__init__.py` 파일로 적절한 패키지 구조 생성

### 2. 데이터 분리
- **data/** 폴더에 모든 TSV 데이터 파일 이동
- 데이터와 코드의 명확한 분리

### 3. 문서화
- **docs/** 폴더에 문서 파일 이동
- **README.md** 추가 (프로젝트 설명, 설치 및 실행 방법)
- **run.sh** 스크립트 추가 (간편한 실행)

### 4. Import 경로 수정
- `app.py`: `from data_loader import ...` → `from utils.data_loader import ...`
- `data_loader.py`: 상대 경로 → 절대 경로로 데이터 파일 참조

## ✅ 테스트 완료

새로운 구조로 Streamlit 앱이 정상적으로 실행되는 것을 확인했습니다.

```bash
# 실행 중인 서버
conda run -n brocelona_scoreboard streamlit run src/app.py --server.port 8501
```

서버 주소: http://localhost:8501

## 📝 이후 작업 방법

### 데이터 업데이트
새로운 경기 결과나 출석 데이터를 추가하려면 `data/` 폴더의 TSV 파일을 수정하세요.

### 코드 수정
- 메인 앱 로직: `src/app.py`
- 데이터 처리 로직: `src/utils/data_loader.py`
- 새로운 유틸리티 추가: `src/utils/` 폴더에 새 파일 생성

### 실행
```bash
# 방법 1: 스크립트 사용
./run.sh

# 방법 2: 직접 실행
streamlit run src/app.py --server.port 8501

# 방법 3: Conda 환경
conda run -n brocelona_scoreboard streamlit run src/app.py --server.port 8501
```

## 🎯 장점

1. **유지보수성 향상**: 코드, 데이터, 문서가 명확히 분리됨
2. **확장성**: 새로운 기능 추가가 용이한 모듈 구조
3. **가독성**: 프로젝트 구조가 직관적이고 이해하기 쉬움
4. **재사용성**: utils 패키지로 함수 재사용 용이
5. **표준 준수**: Python 프로젝트 모범 사례 적용
