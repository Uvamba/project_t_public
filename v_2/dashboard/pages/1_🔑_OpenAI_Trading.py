"""
OpenAI GPT-4 기반 트레이딩 페이지
실시간 시장 분석과 거래 실행을 제공

# 주요 기능:
- API 키 설정 및 관리
  - OpenAI API 키 입력
  - 거래 설정 구성

- 시장 데이터 표시
  - 실시간 가격 차트
  - 거래량 정보
  - 포지션 상태

- GPT-4 분석
  - 시장 상황 분석
  - 매매 전략 제안
  - 리스크 평가

- 거래 실행
  - 자동 거래 실행
  - 거래 내역 표시
  - 성과 분석
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import yaml
from models.llm_interface import LLMInterface
from strategies.llm_strategy import LLMStrategy
from scripts.fetch_data import fetch_market_data
from strategies.binance_client import BinanceClient

def load_config():
    """설정 파일 로드"""
    with open('utils/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def save_config(config):
    """설정 파일 저장"""
    with open('utils/config.yaml', 'w') as file:
        yaml.dump(config, file)

def main():
    """
    메인 대시보드 표시
    
    Sections:
    1. API 설정
       - OpenAI API 키 관리
       - 거래 파라미터 설정
       
    2. 시장 정보
       - 실시간 가격/거래량
       - 포지션 상태
       
    3. GPT-4 분석
       - 시장 분석 결과
       - 매매 전략
       
    4. 거래 통계
       - 수익률 분석
       - 거래 내역
    """
    st.title('🤖 OpenAI 트레이딩')
    
    # 설정 파일 로드
    config = load_config()
    
    # OpenAI API 키 설정
    st.sidebar.header('⚙️ API 설정')
    openai_api_key = st.sidebar.text_input(
        'OpenAI API Key',
        value=config['openai'].get('api_key', ''),
        type='password'
    )
    
    if not openai_api_key:
        st.warning('⚠️ OpenAI API 키를 입력해주세요!')
        return
    
    # 거래 설정
    st.sidebar.header('거래 설정')
    
    interval = st.sidebar.slider(
        '분석 주기 (초)',
        min_value=5,
        max_value=60,
        value=config['trading']['interval']
    )
    
    min_amount = st.sidebar.number_input(
        '최소 거래량 (BTC)',
        min_value=0.001,
        max_value=0.1,
        value=config['trading']['min_amount']
    )
    
    max_amount = st.sidebar.number_input(
        '최대 거래량 (BTC)',
        min_value=0.1,
        max_value=1.0,
        value=config['trading']['max_amount']
    )
    
    # LLM 설정
    st.sidebar.header('LLM 설정')
    temperature = st.sidebar.slider(
        'Temperature',
        min_value=0.0,
        max_value=1.0,
        value=config['llm']['temperature']
    )
    
    # 설정 저장
    if st.sidebar.button('설정 저장'):
        config['openai']['api_key'] = openai_api_key
        config['trading'].update({
            'interval': interval,
            'min_amount': min_amount,
            'max_amount': max_amount
        })
        config['llm']['temperature'] = temperature
        save_config(config)
        st.sidebar.success('✅ 설정이 저장되었습니다!')
    
    # 바이낸스 클라이언트 초기화
    client = BinanceClient(
        api_key=config['binance']['api_key'],
        secret_key=config['binance']['secret_key'],
        testnet=True
    )
    
    # LLM 전략 초기화
    strategy = LLMStrategy(openai_api_key, client)
    
    # 실시간 정보 표시
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # 시장 데이터 수집
        market_data = fetch_market_data()
        
        # LLM 분석 실행
        llm_output = strategy.llm.generate_strategy(market_data)
        trading_signal = strategy.generator.parse_strategy(llm_output)
        
        # 현재 포지션 정보
        position = client.get_position('BTC/USDT')
        
        with col1:
            st.metric(
                label="현재가",
                value=f"${market_data['price']:,.2f}"
            )
        
        with col2:
            st.metric(
                label="BTC 보유량",
                value=f"{position['base']['total']:.3f} BTC"
            )
        
        with col3:
            st.metric(
                label="USDT 잔고",
                value=f"${position['quote']['free']:,.2f}"
            )
        
        with col4:
            st.metric(
                label="매매신호",
                value=trading_signal['action'].upper()
            )
        
        # LLM 분석 결과
        st.subheader("🤖 GPT-4 분석")
        st.text_area(
            "분석 결과",
            llm_output,
            height=100
        )
        
        # 차트 섹션
        st.subheader("📈 시장 데이터")
        
        # OHLCV 데이터 가져오기
        ohlcv = client.get_ohlcv('BTC/USDT', '1h', 100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # 캔들스틱 차트
        fig = go.Figure(data=[
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='OHLC'
            )
        ])
        
        fig.update_layout(
            title="BTC/USDT 가격 차트",
            yaxis_title="가격 (USDT)",
            xaxis_title="시간",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 거래 통계
        st.subheader("📊 거래 통계")
        stats = client.get_trade_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 거래 횟수", f"{stats['total_trades']}회")
            st.metric("매수 횟수", f"{stats['buy_trades']}회")
        
        with col2:
            st.metric("거래 성공률", f"{stats['success_rate']:.1f}%")
            st.metric("매도 횟수", f"{stats['sell_trades']}회")
        
        with col3:
            st.metric("총 거래대금", f"${stats['total_volume']:,.2f}")
            st.metric("평균 거래량", f"{stats['avg_trade_size']:.4f} BTC")
        
        # 자동 새로고침
        time.sleep(interval)
        st.rerun()
        
    except Exception as e:
        st.error(f"에러 발생: {e}")
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main() 