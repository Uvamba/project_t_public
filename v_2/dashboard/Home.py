"""
트레이딩 봇 메인 대시보드
시스템 설정과 실행 환경을 관리하는 진입점

# 주요 기능:
- 실행 환경 관리
  - 테스트넷/실거래 선택
  - API 선택 (Groq/OpenAI)
  - 설정 저장/로드

- 시스템 상태 표시
  - 현재 실행 상태
  - 에러/경고 메시지
  - 버전 정보

- 거래 모니터링
  - 실시간 거래 현황
  - 포지션 정보
  - 수익률 분석
"""

import streamlit as st
import yaml
import time
import os
import subprocess
import pandas as pd
import plotly.graph_objects as go
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategies.binance_client import BinanceClient
from scripts.fetch_data import fetch_market_data
from models.groq_interface import GroqInterface
from models.openai_interface import OpenAIInterface
from strategies.technical_indicators import TechnicalAnalysis
from utils.config import load_config

def run_trading_page(page_name):
    """트레이딩 페이지 실행"""
    script_path = os.path.join('dashboard', 'pages', page_name)
    subprocess.Popen(['streamlit', 'run', script_path])

def display_groq_trading():
    """Groq 트레이딩 화면 표시"""
    try:
        # 설정 파일 로드
        config = load_config()
        
        # Groq API 키 설정
        st.sidebar.header('⚙️ API 설정')
        groq_api_key = st.sidebar.text_input(
            'Groq API Key',
            value=config['groq'].get('api_key', ''),
            type='password'
        )
        
        # 거래 설정
        st.sidebar.header('거래 설정')
        interval = st.sidebar.slider(
            '분석 주기 (초)',
            min_value=5,
            max_value=60,
            value=config['trading']['interval']
        )
        
        # 바이낸스 클라이언트 초기화
        client = BinanceClient(
            api_key=config['binance'][st.session_state.environment]['api_key'],
            secret_key=config['binance'][st.session_state.environment]['secret_key'],
            testnet=(st.session_state.environment == 'testnet')
        )
        
        # 시장 데이터 수집
        market_data = fetch_market_data()
        
        # 현재 포지션 정보
        position = client.get_position('BTC/USDT')
        
        # 지표 표시
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("현재가", f"${market_data['price']:,.2f}")
        with col2:
            st.metric("BTC 보유량", f"{position['base']['total']:.3f} BTC")
        with col3:
            st.metric("USDT 잔고", f"${position['quote']['free']:,.2f}")
        with col4:
            st.metric("거래량", f"${market_data['volume']:,.2f}")
        
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
        
        # LLM 분석 섹션
        st.subheader("🤖 LLM 분석")
        
        # Groq 인터페이스 초기화
        groq = GroqInterface(groq_api_key)
        
        # 시장 분석 실행
        with st.spinner("시장 분석 중..."):
            analysis = groq.analyze_market(market_data, df)
            st.markdown(analysis)
        
        # 거래 통계
        st.subheader("📊 거래 통계")
        stats = client.get_trade_stats()
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("총 거래 횟수", f"{stats['total_trades']}회")
            st.metric("매수 횟수", f"{stats['buy_trades']}회")
        
        with stat_col2:
            st.metric("거래 성공률", f"{stats['success_rate']:.1f}%")
            st.metric("매도 횟수", f"{stats['sell_trades']}회")
        
        with stat_col3:
            st.metric("총 거래대금", f"${stats['total_volume']:,.2f}")
            st.metric("평균 거래량", f"{stats['avg_trade_size']:.4f} BTC")
            
        # 자동 새로고침
        time.sleep(interval)
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"에러 발생: {e}")
        time.sleep(5)
        st.experimental_rerun()

def display_openai_trading():
    """OpenAI 트레이딩 화면 표시"""
    try:
        # 설정 파일 로드
        config = load_config()
        
        # OpenAI API 키 설정
        st.sidebar.header('⚙️ API 설정')
        openai_api_key = st.sidebar.text_input(
            'OpenAI API Key',
            value=config['openai'].get('api_key', ''),
            type='password'
        )
        
        # 거래 설정
        st.sidebar.header('거래 설정')
        interval = st.sidebar.slider(
            '분석 주기 (초)',
            min_value=5,
            max_value=60,
            value=config['trading']['interval']
        )
        
        # 바이낸스 클라이언트 초기화
        client = BinanceClient(
            api_key=config['binance'][st.session_state.environment]['api_key'],
            secret_key=config['binance'][st.session_state.environment]['secret_key'],
            testnet=(st.session_state.environment == 'testnet')
        )
        
        # 시장 데이터 수집
        market_data = fetch_market_data()
        
        # 현재 포지션 정보
        position = client.get_position('BTC/USDT')
        
        # 지표 표시
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("현재가", f"${market_data['price']:,.2f}")
        with col2:
            st.metric("BTC 보유량", f"{position['base']['total']:.3f} BTC")
        with col3:
            st.metric("USDT 잔고", f"${position['quote']['free']:,.2f}")
        with col4:
            st.metric("거래량", f"${market_data['volume']:,.2f}")
            
        # 자동 새로고침
        time.sleep(interval)
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"에러 발생: {e}")
        time.sleep(5)
        st.experimental_rerun()

def display_charts(df):
    """
    차트 시각화 함수
    
    Args:
        df (pd.DataFrame): OHLCV 데이터와 기술적 지표가 포함된 DataFrame
        
    표시되는 차트:
    1. BTC/USDT 캔들스틱
    2. RSI (14) - 과매수/과매도 기준선 포함
    3. MACD - 시그널선과 히스토그램
    """
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
    st.plotly_chart(candlestick, use_container_width=True)
    
    # RSI와 MACD 차트를 나란히 표시
    col1, col2 = st.columns(2)
    
    with col1:
        rsi = go.Figure()
        rsi.add_trace(go.Scatter(
            x=df.index,
            y=df['RSI'], 
            name='RSI',
            line=dict(color='#2962FF', width=2)
        ))
        rsi.add_hline(
            y=70, 
            line_dash="dash", 
            line_color="red",
            annotation_text="과매수",
            annotation_position="right"
        )
        rsi.add_hline(
            y=30, 
            line_dash="dash", 
            line_color="green",
            annotation_text="과매도",
            annotation_position="right"
        )
        rsi.update_layout(
            title="RSI (14)",
            height=250,
            xaxis_title="시간",
            yaxis_title="RSI",
            plot_bgcolor='white',
            yaxis=dict(gridcolor='lightgrey')
        )
        st.plotly_chart(rsi, use_container_width=True)
    
    with col2:
        macd = go.Figure()
        macd.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD'], 
            name='MACD',
            line=dict(color='#2962FF', width=2)
        ))
        macd.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD_Signal'], 
            name='Signal',
            line=dict(color='#FF6D00', width=2)
        ))
        macd.add_bar(
            x=df.index,
            y=df['MACD_Hist'], 
            name='Histogram',
            marker_color=['red' if x < 0 else 'green' for x in df['MACD_Hist']]
        )
        macd.update_layout(
            title="MACD",
            height=250,
            xaxis_title="시간",
            yaxis_title="MACD",
            plot_bgcolor='white',
            yaxis=dict(gridcolor='lightgrey')
        )
        st.plotly_chart(macd, use_container_width=True)

def display_signals(signals):
    st.subheader("📊 기술적 분석 시그널")
    
    for signal in signals:
        color = (
            "success" if signal['action'] == 'consider_buy'
            else "error" if signal['action'] == 'consider_sell'
            else "info"
        )
        
        message = (
            f"**{signal['indicator']}**: {signal['signal']} "
            f"({signal['strength']} 강도) → "
            f"{'🔵 매수 고려' if signal['action'] == 'consider_buy' else '🔴 매도 고려'}"
        )
        
        st.markdown(
            f"""<div style='padding: 10px; border-radius: 5px; 
            background-color: {"#E8F5E9" if color == "success" else "#FFEBEE" if color == "error" else "#E3F2FD"}'>
            {message}</div>""",
            unsafe_allow_html=True
        )

def start_trading(client, llm_provider):
    """
    트레이딩 실행 함수
    
    Args:
        client: BinanceClient 인스턴스
        llm_provider: 사용할 LLM 제공자
    """
    try:
        # 시장 데이터 가져오기
        df = fetch_market_data()
        
        # 기술적 분석 수행
        analysis = TechnicalAnalysis(df)
        analysis_result = analysis.analyze_rsi_macd()
        
        # 현재 포지션 정보
        position = client.get_position('BTC/USDT')
        
        # 지표 표시
        current_data = df.iloc[-1]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("현재가", f"${current_data['close']:,.2f}")
        with col2:
            st.metric("BTC 보유량", f"{position['base']['total']:.3f} BTC")
        with col3:
            st.metric("USDT 잔고", f"${position['quote']['free']:,.2f}")
        with col4:
            st.metric("거래량", f"${current_data['volume']:,.2f}")
        
        # 차트와 시그널 표시
        display_charts(analysis_result['historical_data'])
        
        # 기술적 분석 결과 표시
        st.subheader("📊 기술적 분석 시그널")
        for signal in analysis_result['signals']:
            st.info(f"**{signal['indicator']}**: {signal['signal']} ({signal['strength']} 강도) → {'🔵 매수 고려' if signal['action'] == 'consider_buy' else '🔴 매도 고려'}")
        
        # 현재 데이터 변환
        current_data = {
            'price': df['close'].iloc[-1],
            'volume': df['volume'].iloc[-1],
            'bid': df['close'].iloc[-1] * 0.9999,
            'ask': df['close'].iloc[-1] * 1.0001
        }
        
        # LLM 분석 실행 및 표시
        st.subheader("🤖 LLM 분석")
        config = load_config()
        llm = GroqInterface(config['groq']['api_key']) if llm_provider == "Groq" else OpenAIInterface(config['openai']['api_key'])
        llm_analysis = llm.analyze_market(current_data, analysis_result)
        st.write(llm_analysis)
        
        # 시장 트렌드 표시
        st.subheader("📈 시장 트렌드")
        st.markdown(
            f"""<div style='padding: 10px; border-radius: 5px; 
            background-color: #F5F5F5'>
            {analysis_result['trend']['description'].upper()}</div>""",
            unsafe_allow_html=True
        )
        
        # 자동 새로고침
        time.sleep(config['trading']['interval'])
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"에러 발생: {e}")
        time.sleep(5)
        st.experimental_rerun()

def main():
    """
    메인 대시보드 실행 함수
    
    처리 순서:
    1. 설정 로드 및 UI 구성
    2. 시장 데이터 수집
    3. 기술적 분석 수행
    4. LLM 분석 실행
    5. 결과 표시 및 자동 갱신
    """
    st.title('🤖 암호화폐 트레이딩 봇')
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 실행 환경 설정")
        
        # 환경 선택
        environment = st.radio(
            "거래 환경 선택",
            ["테스트넷", "실거래"],
            index=0  # 기본값은 테스트넷
        )
        
        # API 선택
        llm_provider = st.radio(
            "LLM 선택",
            ["Groq", "OpenAI GPT-4"],
            index=0
        )
        
        # API 키 입력
        st.header("🔑 API 키 설정")
        
        # Binance API 키
        binance_api_key = st.text_input(
            "Binance API Key",
            type="password",
            help="Binance API 키를 입력하세요"
        )
        binance_secret_key = st.text_input(
            "Binance Secret Key",
            type="password",
            help="Binance Secret 키를 입력하세요"
        )
        
        # LLM API 키
        llm_api_key = st.text_input(
            f"{llm_provider} API Key",
            type="password",
            help=f"{llm_provider} API 키를 입력하세요"
        )
        
        # 실행 버튼
        if st.button('트레이딩 시작'):
            if not (binance_api_key and binance_secret_key and llm_api_key):
                st.error("모든 API 키를 입력해주세요!")
            else:
                # 클라이언트 초기화
                client = BinanceClient(
                    api_key=binance_api_key,
                    secret_key=binance_secret_key,
                    testnet=(environment == "테스트넷")
                )
                
                # 환경변수 설정
                if llm_provider == "Groq":
                    os.environ['GROQ_API_KEY'] = llm_api_key
                else:
                    os.environ['OPENAI_API_KEY'] = llm_api_key
                
                # 트레이딩 시작
                start_trading(client, llm_provider)
        else:
            st.info('👈 API 키를 입력하고 트레이딩을 시작하세요.')

if __name__ == "__main__":
    main() 