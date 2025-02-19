"""
Groq LLM 기반 트레이딩 페이지
실시간 시장 분석과 거래 실행을 제공

# 주요 기능:
- API 키 설정 및 관리
- 실시간 시장 데이터 표시
- LLM 기반 시장 분석
- 거래 통계 시각화
- 자동 거래 실행
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import yaml
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 path에 추가
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from models.groq_interface import GroqInterface
from scripts.fetch_data import fetch_market_data
from strategies.binance_client import BinanceClient
from strategies.technical_indicators import TechnicalAnalysis

def load_config():
    """설정 파일 로드"""
    with open('utils/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def save_config(config):
    """설정 파일 저장"""
    with open('utils/config.yaml', 'w') as file:
        yaml.dump(config, file)

def display_charts(df):
    # 캔들스틱 차트
    candlestick = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC'
        )
    ])
    candlestick.update_layout(title="BTC/USDT 가격 차트", height=400)
    
    # RSI 차트
    rsi = go.Figure()
    rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI'))
    rsi.add_hline(y=70, line_dash="dash", line_color="red")
    rsi.add_hline(y=30, line_dash="dash", line_color="green")
    rsi.update_layout(title="RSI (14)", height=200)
    
    # MACD 차트
    macd = go.Figure()
    macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD'))
    macd.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Signal'))
    macd.add_bar(x=df.index, y=df['MACD_Hist'], name='Histogram')
    macd.update_layout(title="MACD", height=200)
    
    return candlestick, rsi, macd

def main():
    """
    메인 대시보드 표시
    
    1. API 설정 섹션
        - Groq API 키 입력
        - 거래 설정 (간격, 거래량 등)
        
    2. 시장 정보 섹션
        - 현재가, 거래량 표시
        - 포지션 정보 표시
        
    3. 분석 섹션
        - LLM 기반 시장 분석
        - 캔들스틱 차트
        - 거래량 차트
        
    4. 통계 섹션
        - 거래 성과 지표
        - 수익률 분석
    """
    st.title('🤖 Groq 트레이딩')
    
    # 설정 파일 로드
    config = load_config()
    
    # Groq API 키 설정
    st.sidebar.header('⚙️ API 설정')
    groq_api_key = st.sidebar.text_input(
        'Groq API Key',
        value=config['groq'].get('api_key', ''),
        type='password'
    )
    
    if not groq_api_key:
        st.warning('⚠️ Groq API 키를 입력해주세요!')
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
        config['groq']['api_key'] = groq_api_key
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
        api_key=config['binance'][st.session_state.environment]['api_key'],
        secret_key=config['binance'][st.session_state.environment]['secret_key'],
        testnet=(st.session_state.environment == 'testnet')
    )
    
    # Groq 인터페이스 초기화
    groq = GroqInterface(groq_api_key)
    
    # 실시간 정보 표시
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # 시장 데이터 수집
        market_data = fetch_market_data()
        
        # Groq 분석 실행
        analysis = groq.generate_strategy(market_data)
        
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
                label="거래량",
                value=f"${market_data['volume']:,.2f}"
            )
        
        # 차트 표시
        candlestick, rsi, macd = display_charts(analysis['chart_data'])
        st.plotly_chart(candlestick, use_container_width=True)
        st.plotly_chart(rsi, use_container_width=True)
        st.plotly_chart(macd, use_container_width=True)
        
        # LLM 분석 결과 표시
        st.subheader("🤖 Groq 분석")
        st.write(analysis['llm_analysis'])
        
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