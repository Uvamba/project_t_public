"""
Groq LLM API 인터페이스
시장 데이터 분석과 매매 전략 생성을 위한 LLM 통신 모듈

주요 기능:
1. API 통신 관리
2. 프롬프트 생성 및 최적화
3. 응답 처리 및 분석
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
            
        초기화 항목:
        - API 엔드포인트 설정
        - 인증 헤더 구성
        - 모델 파라미터 설정
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
        
    def analyze_market(self, market_data, analysis_result):
        """
        시장 데이터 분석 및 매매 전략 생성
        
        Args:
            market_data (dict): 현재 시장 데이터
                - price: 현재가
                - volume: 거래량
                - bid/ask: 호가 정보
            analysis_result (dict): 기술적 분석 결과
                - rsi: RSI 값
                - macd: MACD 관련 지표
                - signals: 매매 신호
                - trend: 시장 트렌드
                
        Returns:
            str: LLM이 생성한 시장 분석과 매매 전략
        """
        # 기술적 지표 값들
        rsi = analysis_result['rsi']
        macd = analysis_result['macd']
        macd_signal = analysis_result['macd_signal']
        macd_hist = analysis_result['macd_hist']
        
        # LLM 프롬프트 생성
        prompt = f"""
현재 비트코인 시장 상황을 분석해주세요:

현재가: ${market_data['price']:,.2f}
거래량: ${market_data['volume']:,.2f}

기술적 지표:
1. RSI: {rsi:.2f}
   - 과매수(70) / 과매도(30) 기준
   - 현재 상태: {"과매수" if rsi > 70 else "과매도" if rsi < 30 else "중립"}

2. MACD
   - MACD: {macd:.4f}
   - Signal: {macd_signal:.4f}
   - Histogram: {macd_hist:.4f}
   - 상태: {"상승추세" if macd_hist > 0 else "하락추세"}

트렌드: {analysis_result['trend']['description']}

위 데이터를 바탕으로:
1. 현재 시장 상황 요약
2. 단기 매매 전략 제안
3. 주의해야 할 리스크
를 제시해주세요.
"""
        
        # API 호출 및 응답 처리
        try:
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
                "max_tokens": 1000
            }
            
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