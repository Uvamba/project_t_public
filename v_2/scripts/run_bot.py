"""
트레이딩 봇 실행 스크립트
전체 시스템의 실행과 모니터링을 담당

# 주요 기능:
- 시스템 초기화
  - 설정 로드
  - API 연결
  - 로깅 설정

- 거래 실행
  - 시장 데이터 수집
  - 전략 실행
  - 주문 관리

- 모니터링
  - 성능 추적
  - 에러 감지
  - 상태 보고
"""

import time
from pathlib import Path
import yaml
import logging

from models.groq_interface import GroqInterface
from strategies.binance_client import BinanceClient
from strategies.llm_strategy import LLMStrategy
from scripts.fetch_data import fetch_market_data
from utils.logger import setup_logger

def main():
    """
    메인 실행 함수
    
    1. 설정 파일 로드
    2. 로깅 시스템 초기화
    3. API 클라이언트 설정
    4. 거래 루프 실행
    """
    # 설정 로드
    config = yaml.safe_load(open('utils/config.yaml'))
    
    # 로거 설정
    logger = setup_logger()
    
    try:
        # 클라이언트 초기화
        client = BinanceClient(
            api_key=config['binance']['testnet']['api_key'],
            secret_key=config['binance']['testnet']['secret_key'],
            testnet=True
        )
        
        # 전략 초기화
        strategy = LLMStrategy(
            api_key=config['groq']['api_key'],
            client=client
        )
        
        # 거래 루프
        while True:
            try:
                # 시장 데이터 수집
                market_data = fetch_market_data()
                
                # 전략 실행
                order = strategy.execute(market_data)
                
                if order:
                    logger.info(f"주문 실행: {order}")
                    
                # 대기
                time.sleep(config['trading']['interval'])
                
            except Exception as e:
                logger.error(f"거래 중 오류: {e}")
                time.sleep(5)
                
    except Exception as e:
        logger.error(f"시스템 오류: {e}")
        
if __name__ == "__main__":
    main() 