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
    """
    실시간 시장 데이터 수집
    
    Returns:
        dict: {
            "timestamp": 현재시각,
            "price": 현재가,
            "bid": 매수호가,
            "ask": 매도호가,
            "volume": 거래량
        }
    """
    # 데이터 디렉토리 확인
    ensure_data_dir()
    
    config = load_config()
    environment = st.session_state.environment
    
    # 바이낸스 클라이언트 설정
    if environment == 'testnet':
        exchange = ccxt.binance({
            'apiKey': config['binance'][environment]['api_key'],
            'secret': config['binance'][environment]['secret_key'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True,
                'testnet': True,
                'url': 'https://testnet.binancefuture.com'
            }
        })
    else:
        exchange = ccxt.binance({
            'apiKey': config['binance'][environment]['api_key'],
            'secret': config['binance'][environment]['secret_key'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True
            }
        })
    
    # 시장 데이터 수집
    symbol = 'BTC/USDT'
    ticker = exchange.fetch_ticker(symbol)
    order_book = exchange.fetch_order_book(symbol)
    
    # 데이터 구조화
    data = {
        "timestamp": datetime.now(),
        "price": ticker['last'],
        "bid": order_book['bids'][0][0] if order_book['bids'] else None,
        "ask": order_book['asks'][0][0] if order_book['asks'] else None,
        "volume": ticker['quoteVolume']
    }
    
    # CSV 파일에 저장
    df = pd.DataFrame([data])
    df.to_csv('data/live_data.csv', mode='a', header=False, index=False)
    
    return data 