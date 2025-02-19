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
        # 메인 컨테이너에 결과 표시
        main_container = st.container()
        
        with main_container:
            # 설정 파일 로드
            config = load_config()
            
            # 거래 설정
            interval = st.slider(
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

def start_trading(client, llm_provider, trading_interval):
    """
    트레이딩 실행 함수
    """
    try:
        # 메인 컨테이너에 결과 표시
        main_container = st.container()
        
        with main_container:
            # 1. 시장 데이터 수집
            df = fetch_market_data()
            
            # 2. 기술적 분석 수행
            analysis = TechnicalAnalysis(df)
            analysis_result = analysis.analyze_rsi_macd()
            
            # 3. 현재 포지션 및 기본 지표 표시
            position = client.get_position('BTC/USDT')
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
            
            # 4. 차트 표시
            display_charts(analysis_result['historical_data'])
            
            # 5. LLM 분석 수행
            current_data = {
                'price': df['close'].iloc[-1],
                'volume': df['volume'].iloc[-1],
                'bid': df['close'].iloc[-1] * 0.9999,
                'ask': df['close'].iloc[-1] * 1.0001
            }
            
            config = load_config()
            llm = GroqInterface(config['groq']['api_key']) if llm_provider == "Groq" else OpenAIInterface(config['openai']['api_key'])
            llm_analysis = llm.analyze_market(current_data, analysis_result)
            
            # LLM 분석 결과 처리
            if isinstance(llm_analysis, str):
                llm_signal = 'hold'
                llm_analysis_text = llm_analysis
            else:
                llm_signal = llm_analysis.get('action', 'hold')
                llm_analysis_text = str(llm_analysis)
            
            # 6. 교차 검증 및 매매 결정
            technical_signal = analysis_result['signals'][0]['action']
            
            # 7. 분석 결과 표시
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 기술적 분석")
                st.write(f"시그널: {technical_signal}")
                display_signals(analysis_result['signals'])
                
            with col2:
                st.subheader("🤖 LLM 분석")
                st.write(f"제안: {llm_signal}")
                st.write(llm_analysis_text)
            
            # 8. 시장 트렌드 표시
            st.subheader("📈 시장 트렌드")
            st.markdown(
                f"""<div style='padding: 10px; border-radius: 5px; 
                background-color: #F5F5F5'>
                {analysis_result['trend']['description'].upper()}</div>""",
                unsafe_allow_html=True
            )
            
            # 9. 매매 실행 (시그널이 일치할 경우)
            if technical_signal == llm_signal and technical_signal != 'hold':
                st.success(f"매매 시그널 일치: {technical_signal}")
            else:
                st.info("현재 매매 시그널이 불일치하거나 관망 중입니다.")
        
        # 자동 갱신
        time.sleep(trading_interval)
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"에러 발생: {e}")
        time.sleep(5)
        st.experimental_rerun()

def check_password():
    """
    비밀번호 확인 함수
    """
    # 세션 상태 초기화
    if 'password_correct' not in st.session_state:
        st.session_state.password_correct = False
    
    # 이미 인증된 경우
    if st.session_state.password_correct:
        return True
    
    # 비밀번호 입력
    st.title('🔒 트레이딩 봇 로그인')
    password = st.text_input(
        "비밀번호를 입력하세요", 
        type="password",
        help="관리자에게 문의하세요"
    )
    
    # 비밀번호 확인 (환경변수에서 가져오기, 없으면 기본값 사용)
    if password == os.environ.get('APP_PASSWORD', 'trading2024!'):
        st.session_state.password_correct = True
        return True
    
    if password:
        st.error("비밀번호가 일치하지 않습니다")
    return False

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
    # 비밀번호 확인
    if not check_password():
        st.stop()  # 비밀번호가 틀리면 여기서 실행 중단
    
    # 메인 타이틀
    st.title('🤖 암호화폐 트레이딩 봇')
    
    # 메인 컨테이너 (결과 표시용)
    main_container = st.container()
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 실행 환경 설정")
        
        # 환경 선택
        environment = st.radio(
            "거래 환경 선택",
            ["테스트넷", "실거래"],
            index=0
        )
        
        # API 선택
        llm_provider = st.radio(
            "LLM 선택",
            ["Groq", "OpenAI GPT-4"],
            index=0
        )
        
        # 거래 설정
        st.header("⚡ 거래 설정")
        trading_interval = st.slider(
            "거래 주기 (초)",
            min_value=10,
            max_value=300,
            value=60,
            step=10,
            help="각 거래 분석 사이의 대기 시간"
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
                
                # 트레이딩 시작 (거래 주기 전달)
                with main_container:
                    start_trading(client, llm_provider, trading_interval)
        else:
            with main_container:
                st.info('👈 API 키를 입력하고 트레이딩을 시작하세요.')

if __name__ == "__main__":
    main() 