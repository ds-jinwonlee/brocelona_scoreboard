#!/bin/bash

# Brocelona Score Dashboard 실행 스크립트

# 현재 디렉토리로 이동
cd "$(dirname "$0")"

# Streamlit 앱 실행
streamlit run src/app.py --server.port 8501
