"""
LLM 기반 트레이딩 봇 대시보드
실시간 모니터링 및 설정 관리
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

def load_config():
    """설정 파일 로드"""
    with open('utils/config.yaml', 'r') as file:
        return yaml.safe_load(file)

def save_config(config):
    """설정 파일 저장"""
    with open('utils/config.yaml', 'w') as file:
        yaml.dump(config, file)

def main():
    st.title('🤖 LLM 트레이딩 봇 대시보드')
    
    # 설정 파일 로드
    config = load_config()
    
    # 사이드바: 설정
    st.sidebar.header('⚙️ 설정')
    
    # API 키 설정
    openai_api_key = st.sidebar.text_input(
        'OpenAI API Key',
        value=config['openai']['api_key'],
        type='password'
    )
    
    # 거래 설정
    st.sidebar.subheader('거래 설정')
    
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
    st.sidebar.subheader('LLM 설정')
    
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
    
    # 메인 화면: 실시간 정보
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # 시장 데이터 수집
        market_data = fetch_market_data()
        
        # LLM 전략 실행
        strategy = LLMStrategy(openai_api_key, None)  # client는 나중에 추가
        llm_output = strategy.llm.generate_strategy(market_data)
        trading_signal = strategy.generator.parse_strategy(llm_output)
        
        # 지표 표시
        with col1:
            st.metric(
                label="현재가",
                value=f"${market_data['price']:,.2f}"
            )
        
        with col2:
            st.metric(
                label="거래량",
                value=f"${market_data['volume']:,.2f}"
            )
        
        with col3:
            st.metric(
                label="매매신호",
                value=trading_signal['action'].upper()
            )
        
        with col4:
            st.metric(
                label="제안수량",
                value=f"{trading_signal['amount']:.3f} BTC"
            )
        
        # LLM 분석 결과
        st.subheader("🤖 LLM 분석")
        st.text_area(
            "GPT-4 분석 결과",
            llm_output,
            height=100
        )
        
        # 차트 섹션
        st.subheader("📈 시장 데이터")
        
        # 실시간 데이터 로드
        df = pd.read_csv('data/live_data.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 가격 차트
        fig = go.Figure(data=[
            go.Scatter(
                x=df['timestamp'],
                y=df['price'],
                name='가격',
                line=dict(color='blue')
            )
        ])
        
        fig.update_layout(
            title="BTC/USDT 가격 추이",
            height=400,
            xaxis_title="시간",
            yaxis_title="가격 (USDT)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 거래 이력
        st.subheader("📝 거래 이력")
        
        # 로그 파일 읽기
        log_file = f"data/logs/trading_{datetime.now().strftime('%Y%m%d')}.log"
        try:
            with open(log_file, 'r') as f:
                logs = f.readlines()[-10:]  # 최근 10개 로그
                for log in logs:
                    st.text(log.strip())
        except FileNotFoundError:
            st.info("아직 거래 이력이 없습니다.")
        
        # 자동 새로고침
        time.sleep(interval)
        st.rerun()
        
    except Exception as e:
        st.error(f"에러 발생: {e}")
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main() 