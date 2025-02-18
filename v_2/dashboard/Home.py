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

def load_config():
    """설정 파일 로드"""
    with open('utils/config.yaml', 'r') as file:
        return yaml.safe_load(file)

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

def main():
    st.title('🤖 암호화폐 트레이딩 봇')
    
    # 세션 상태 초기화
    if 'environment' not in st.session_state:
        st.session_state.environment = None
    if 'api_choice' not in st.session_state:
        st.session_state.api_choice = None
    
    st.markdown("""
    ## 시스템 개요
    이 트레이딩 봇은 LLM을 활용하여 암호화폐 시장을 분석하고 매매 전략을 생성합니다.
    """)
    
    # 사이드바 설정
    st.sidebar.header("⚙️ 실행 설정")
    
    # 실행 환경 선택
    st.sidebar.subheader("1️⃣ 실행 환경")
    env_col1, env_col2 = st.sidebar.columns(2)
    
    with env_col1:
        testnet = st.checkbox("테스트넷", 
                            key="testnet",
                            help="테스트넷에서 실험")
    
    with env_col2:
        livenet = st.checkbox("실제 거래", 
                            key="livenet",
                            help="실제 자금으로 거래")
    
    # API 선택
    st.sidebar.subheader("2️⃣ API 선택")
    api_col1, api_col2 = st.sidebar.columns(2)
    
    with api_col1:
        groq = st.checkbox("Groq API", 
                          key="groq",
                          help="Mixtral-8x7B 모델 사용")
    
    with api_col2:
        openai = st.checkbox("OpenAI API", 
                           key="openai",
                           help="GPT-4 모델 사용")
    
    # 환경 검증
    env_selected = sum([testnet, livenet])
    if env_selected > 1:
        st.sidebar.error("❌ 실행 환경은 하나만 선택해주세요!")
        return
    
    # API 검증
    api_selected = sum([groq, openai])
    if api_selected > 1:
        st.sidebar.error("❌ API는 하나만 선택해주세요!")
        return
        
    # 실행 버튼
    if st.sidebar.button("▶️ 실행", use_container_width=True):
        if env_selected == 0:
            st.sidebar.error("❌ 실행 환경을 선택해주세요!")
            return
            
        if api_selected == 0:
            st.sidebar.error("❌ API를 선택해주세요!")
            return
            
        # 환경 설정
        st.session_state.environment = "testnet" if testnet else "live"
        
        # API 설정
        st.session_state.api_choice = "groq" if groq else "openai"
        
        # 설정 확인
        config = load_config()
        
        # API 키 확인
        if st.session_state.api_choice == "groq":
            if not config['groq']['api_key']:
                st.sidebar.error("❌ Groq API 키가 설정되지 않았습니다!")
                return
        else:
            if not config['openai']['api_key']:
                st.sidebar.error("❌ OpenAI API 키가 설정되지 않았습니다!")
                return
                
        # 바이낸스 API 키 확인
        if not config['binance'][st.session_state.environment]['api_key']:
            st.sidebar.error(f"❌ {st.session_state.environment} 환경의 바이낸스 API 키가 설정되지 않았습니다!")
            return
            
        # 실행 정보 표시
        st.success(f"""
        ✅ 트레이딩 봇이 다음 설정으로 실행됩니다:
        - 실행 환경: {'테스트넷' if testnet else '실제 거래'}
        - 사용 API: {'Groq' if groq else 'OpenAI'}
        """)
        
        # 페이지 선택 저장
        if groq:
            st.session_state.page = 'groq'
        else:
            st.session_state.page = 'openai'
        
        # 새로고침
        st.experimental_rerun()

    # 시스템 상태
    st.sidebar.header('시스템 상태')
    st.sidebar.success('✅ 정상 작동 중')
    
    # 기본 정보
    st.sidebar.info("""
    현재 버전: v2.0
    최근 업데이트: 2025.02
    """)

    # 페이지 표시
    if 'page' in st.session_state:
        if st.session_state.page == 'groq':
            st.title('🤖 Groq 트레이딩')
            # Groq 트레이딩 관련 컴포넌트 표시
            display_groq_trading()
        else:
            st.title('🤖 OpenAI 트레이딩')
            # OpenAI 트레이딩 관련 컴포넌트 표시
            display_openai_trading()

if __name__ == "__main__":
    main() 