"""
바이낸스 시장 데이터 수집 모듈
실시간 가격과 거래 정보를 수집하고 저장

# 주요 기능:
- 시장 데이터 수집
  - 실시간 가격
  - 오더북 정보
  - 거래량 데이터

- 데이터 저장
  - CSV 파일 저장
  - 로그 기록
  - 백업 관리

- 에러 처리
  - 네트워크 오류
  - API 제한
  - 데이터 검증
"""

import ccxt
import pandas as pd
from datetime import datetime
import streamlit as st
import yaml
import os

def load_config():
    """
    설정 파일 로드
    API 키와 거래 설정을 YAML 파일에서 읽어옴
    """
    with open('utils/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def ensure_data_dir():
    """
    데이터 저장용 디렉토리 생성
    - data/: 시장 데이터 저장
    - data/logs/: 로그 파일 저장
    """
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if not os.path.exists(os.path.join(data_dir, 'logs')):
        os.makedirs(os.path.join(data_dir, 'logs'))

def fetch_market_data():
    """시장 데이터 수집"""
    # 바이낸스 API로부터 데이터 가져오기
    client = ccxt.binance()
    
    # OHLCV 데이터 가져오기 (1시간 봉)
    ohlcv = client.fetch_ohlcv('BTC/USDT', '1h', limit=100)
    
    # DataFrame 생성
    df = pd.DataFrame(
        ohlcv,
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )
    
    # 타임스탬프를 datetime으로 변환
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    return df 