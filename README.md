# 암호화폐 트레이딩 봇 v2.0 (개발 중)

LLM(Large Language Model)을 활용한 암호화폐 자동 거래 시스템입니다.

## ⚠️ 개발 상태
현재 이 프로젝트는 개발 진행 중입니다:
- [x] 기본 프레임워크 설정
- [x] 도커 환경 구성
- [x] Streamlit 웹 인터페이스
- [x] Binance API 연동
  - [x] 테스트넷 연결
  - [x] 시장 데이터 조회
  - [x] 기술적 분석 (RSI, MACD)
- [x] LLM 모델 통합
  - [x] 기술적 지표 기반 분석
  - [x] 매매 전략 제안
- [ ] 실제 거래 실행
- [ ] 백테스팅 기능

## 현재 구현된 기능
1. 하이브리드 분석 시스템
   - 기술적 분석 (RSI, MACD)
   - LLM 기반 전략 분석
   - 교차 검증 매매 결정

2. 실시간 모니터링
   - 캔들스틱 차트
   - RSI/MACD 지표
   - 거래량 분석

3. LLM 기반 분석
   - 기술적 지표 해석
   - 시장 트렌드 분석
   - 리스크 평가

## 매매 프로세스
1. **기술적 분석 단계**
   - RSI/MACD 계산
   - 기술적 시그널 생성
   - 트렌드 분석

2. **LLM 분석 단계**
   - 기술적 지표 해석
   - 시장 상황 분석
   - 매매 전략 제안

3. **매매 결정 단계**
   - 기술적 시그널 검증
   - LLM 분석 검증
   - 최종 매매 결정

## 도커로 실행하기

### 사전 준비사항
- Docker 설치
- Docker Compose 설치
- API 키 준비
  - Binance 테스트넷 API 키/시크릿
  - Groq API 키 또는 OpenAI API 키

### 실행 방법

1. config.yaml 설정:
```bash
# utils 디렉토리로 이동
cd v_2/utils

# config.yaml 파일 생성
cp config.yaml.example config.yaml

# config.yaml 파일에 API 키 입력
vi config.yaml
```

2. 도커 이미지 빌드 및 실행:
```bash
docker-compose up --build
```

3. 웹 브라우저에서 접속:
- http://localhost:8501

### 도커 컨테이너 관리

```bash
# 백그라운드로 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 컨테이너 중지
docker-compose down

# 컨테이너 재시작
docker-compose restart
```

## 수동 설치 방법

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. API 키 설정:
- utils/config.yaml 파일에 API 키 입력
  - Binance 테스트넷 API 키
  - Groq/OpenAI API 키

3. 실행:
```bash
streamlit run dashboard/Home.py
```

## 주요 기능

### 1. LLM 기반 시장 분석
- Groq Mixtral-8x7B 모델 지원
- OpenAI GPT-4 모델 지원
- 실시간 시장 데이터 분석
- 매매 전략 자동 생성

### 2. 거래 실행
- 바이낸스 선물 거래 지원
- 테스트넷/실거래 환경 선택
- 자동 주문 실행
- 포지션 관리

### 3. 실시간 모니터링
- 웹 기반 대시보드
- 실시간 차트 표시
- 거래 내역 추적
- 성과 분석

## 시스템 구조

```
v_2/
├── dashboard/          # 웹 인터페이스
│   ├── Home.py        # 메인 대시보드
│   └── pages/         # 트레이딩 페이지
├── models/            # LLM 모델
│   ├── groq_interface.py
│   ├── llm_interface.py
│   └── graph_api.py
├── scripts/           # 실행 스크립트
│   ├── fetch_data.py  # 데이터 수집
│   └── run_bot.py     # 봇 실행
├── strategies/        # 거래 전략
│   ├── binance_client.py
│   └── llm_strategy.py
└── utils/            # 유틸리티
    ├── config.yaml   # 설정 파일
    └── logger.py     # 로깅
```

## 주의사항

- 실제 거래 시 충분한 테스트 필요
- API 키 보안 주의
- 리스크 관리 설정 필수
- 네트워크 안정성 확인
- 바이낸스 현물 테스트넷 사용
  - GitHub 계정으로 로그인 필요
  - API 키는 월간 데이터 리셋에도 유지
  - 실제 API와 동일한 속도 제한 적용

## 설정 방법

1. config.yaml 파일 생성:
```bash
# utils 디렉토리로 이동
cd v_2/utils

# config.yaml 파일 생성
cp config.yaml.example config.yaml

# config.yaml 파일 편집
vi config.yaml
```

2. API 키 설정:
- config.yaml 파일에 다음 정보를 입력:
  - Binance 테스트넷 API 키/시크릿
  - Groq API 키

## 업데이트 내역

### v2.0 (2025.02)
- Groq Mixtral-8x7B 모델 추가
- 실시간 차트 기능 개선
- 거래 통계 기능 추가
- 에러 처리 강화

## 라이선스

MIT License

## 향후 개발 계획
1. 매매 전략 구현
   - 분석 결과 기반 매매 신호 생성
   - 자동 주문 실행 시스템
   - 포지션 관리 로직

2. 리스크 관리
   - 손실 제한 설정
   - 포지션 사이즈 최적화
   - 자동 스탑로스/익절

3. 백테스팅 시스템
   - 과거 데이터 기반 전략 검증
   - 성과 분석 리포트
   - 전략 최적화
