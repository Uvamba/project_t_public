"""
로깅 시스템
거래 및 시스템 로그 관리

주요 기능:
1. 거래 로그 기록
2. 에러 로깅
3. 성능 메트릭 기록
4. 로그 파일 관리
"""
import logging
from datetime import datetime

def setup_logger():
    """
    로깅 시스템 초기화
    
    설정:
    1. 파일 로거: 일별 로그 파일 생성
    2. 콘솔 로거: 실시간 로그 출력
    3. 로그 레벨: INFO
    4. 로그 포맷: 시간 - 레벨 - 메시지
    
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