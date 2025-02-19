"""
OpenAI GPT-4 API 인터페이스
시장 데이터 분석과 매매 전략 생성을 위한 LLM 통신 모듈
"""

import openai
from typing import Dict, Any

class OpenAIInterface:
    def __init__(self, api_key: str):
        """
        OpenAI API 클라이언트 초기화
        
        Args:
            api_key (str): OpenAI API 인증 키
        """
        self.api_key = api_key
        openai.api_key = api_key
        self.model = "gpt-4"
        
    def analyze_market(self, market_data: Dict[str, Any], analysis_result: Dict[str, Any]) -> str:
        """
        시장 데이터 분석 및 전략 생성
        
        Args:
            market_data: 현재 시장 데이터
            analysis_result: 기술적 분석 결과
            
        Returns:
            str: 분석 결과 및 전략 제안
        """
        prompt = f"""
        현재 시장 상황:
        - 가격: ${market_data['price']:,.2f}
        - 거래량: {market_data['volume']:,.2f}
        
        기술적 분석:
        - RSI: {analysis_result['rsi']}
        - MACD: {analysis_result['macd']}
        
        시그널:
        {', '.join([f"{s['indicator']}: {s['signal']}" for s in analysis_result['signals']])}
        
        트렌드:
        {analysis_result['trend']['description']}
        
        위 데이터를 바탕으로 현재 시장 상황을 분석하고, 
        1. 시장 동향 요약
        2. 단기 매매 전략 제안
        3. 주의해야 할 리스크
        를 제시해주세요.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 암호화폐 트레이딩 전문가입니다."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['choices'][0]['message']['content']
            
        except Exception as e:
            return f"OpenAI API 오류: {str(e)}" 