"""
프로젝트 설치 설정 파일
패키지 메타데이터와 의존성 정의
"""

from setuptools import setup, find_packages

setup(
    name="project_t",  # 패키지 이름
    version="2.0",             # 현재 버전
    packages=find_packages(where="."),  # 자동으로 모든 패키지 탐색
    package_dir={"": "."},
    
    # 필수 의존성 패키지들
    install_requires=[
        "ccxt",        # 암호화폐 거래소 API
        "openai",      # OpenAI API 
        "streamlit",   # 웹 대시보드
        "pandas",      # 데이터 처리
        "plotly",      # 인터랙티브 차트
        "pyyaml",      # YAML 설정 파일
        "python-dotenv",  # 환경 변수
        "requests",    # HTTP 요청
        "altair",      # 데이터 시각화
        "groq"         # Groq API
    ]
) 