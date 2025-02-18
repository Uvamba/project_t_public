"""
Groq API를 사용한 시장 분석 인터페이스
LLM을 활용하여 시장 데이터를 분석하고 매매 전략을 생성하는 클래스
"""

import os
import requests
import json
from datetime import datetime
import pandas as pd

class GroqInterface:
    def __init__(self, api_key):
        """
        Groq API 클라이언트 초기화
        
        Args:
            api_key (str): Groq API 인증 키
        """
        self.api_key = api_key
        # OpenAI 호환 엔드포인트 사용
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        # Mixtral 8x7B 모델 사용 (GPT-4 수준의 성능)
        self.model = "mixtral-8x7b-32768"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def analyze_market(self, market_data, historical_data):
        """
        시장 데이터 분석 및 매매 전략 생성
        
        Args:
            market_data (dict): 현재 시장 데이터
                - price: 현재가
                - volume: 거래량
                - bid: 매수호가
                - ask: 매도호가
            historical_data (pd.DataFrame): OHLCV 과거 데이터
                - timestamp: 시간
                - open: 시가
                - high: 고가
                - low: 저가
                - close: 종가
                - volume: 거래량
        
        Returns:
            str: LLM이 생성한 시장 분석 및 전략 제안
        """
        # 최근 10개 데이터만 사용
        recent_data = historical_data.tail(10)
        
        # 기술적 지표 계산
        volatility = recent_data['close'].std()  # 변동성
        price_change = (market_data['price'] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0] * 100  # 가격 변동률
        
        # LLM 프롬프트 생성
        prompt = f"""
현재 비트코인 시장 상황을 분석하고 매매 전략을 제시해주세요.

현재 시장 데이터:
- 현재가: ${market_data['price']:,.2f}
- 24시간 거래량: ${market_data['volume']:,.2f}
- 최고 매수호가: ${market_data['bid']:,.2f}
- 최저 매도호가: ${market_data['ask']:,.2f}

시장 지표:
- 최근 가격 변동성: {volatility:.2f}
- 가격 변동률: {price_change:.2f}%

이 데이터를 바탕으로:
1. 현재 시장 상황 분석
2. 단기 가격 전망
3. 매매 전략 제안
4. 주의해야 할 리스크
"""
        
        # API 요청 데이터 구성
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "당신은 암호화폐 트레이딩 전문가입니다. 시장 데이터를 분석하고 매매 전략을 제시합니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,  # 적당한 창의성 부여
            "max_tokens": 1000   # 충분한 응답 길이 확보
        }
        
        # API 호출 및 응답 처리
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"분석 중 오류 발생: {str(e)}"

    def generate_strategy(self, market_data):
        """
        간단한 매매 전략 생성
        
        Args:
            market_data (dict): 현재 시장 데이터
        
        Returns:
            str: 매매 전략
        """
        prompt = f"""
현재 비트코인 가격: ${market_data['price']:,.2f}
거래량: ${market_data['volume']:,.2f}

이 상황에서 적절한 매매 전략을 제시해주세요.
"""
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "당신은 암호화폐 트레이딩 전문가입니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"전략 생성 중 오류 발생: {str(e)}" 