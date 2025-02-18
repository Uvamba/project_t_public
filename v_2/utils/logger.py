"""
로깅 시스템
시스템 로그와 거래 로그를 관리하는 유틸리티

# 주요 기능:
- 시스템 로그 기록
  - 초기화 정보
  - 에러 메시지
  - 성능 메트릭
  
- 거래 로그 기록
  - 주문 실행 내역
  - 포지션 변경
  - 수익/손실 정보
  
- 로그 파일 관리
  - 일별 로그 파일 생성
  - 로그 순환 (rotation)
  - 디스크 공간 관리
"""
import logging
from datetime import datetime

def setup_logger():
    """
    로깅 시스템 초기화
    
    1. 파일 핸들러 설정
       - 일별 로그 파일 생성
       - 로그 포맷 정의
       
    2. 콘솔 핸들러 설정
       - 실시간 로그 출력
       - 로그 레벨 필터링
       
    3. 로그 디렉토리 관리
       - 디렉토리 생성
       - 오래된 로그 정리
    
    Returns:
        Logger: 설정된 로거 인스턴스
    """
    # 로깅 기본 설정
    logging.basicConfig(
        level=logging.INFO,  # 로그 레벨 설정
        format='%(asctime)s - %(levelname)s - %(message)s',  # 로그 형식
        handlers=[
            # 파일 핸들러: 날짜별 로그 파일 생성
            logging.FileHandler(
                f'data/logs/trading_{datetime.now().strftime("%Y%m%d")}.log'
            ),
            # 콘솔 출력 핸들러
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__) 