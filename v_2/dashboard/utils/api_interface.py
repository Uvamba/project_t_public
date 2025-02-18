"""
API 인터페이스 관리
OpenAI와 Groq API 연동을 위한 인터페이스
"""

import openai
from models.groq_interface import GroqInterface

class OpenAIInterface:
    """OpenAI API 인터페이스"""
    def __init__(self):
        self.model = "gpt-4"
        
    def generate_strategy(self, market_data):
        """시장 데이터 기반 전략 생성"""
        prompt = f"""
        현재 BTC/USDT 시장 데이터:
        - 현재가: ${market_data['price']:,.2f}
        - 거래량: {market_data['volume']:.2f} BTC
        - 매수호가: ${market_data['bid']:,.2f}
        - 매도호가: ${market_data['ask']:,.2f}

        위 데이터를 분석하여 매매 전략을 제시해주세요.
        """
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']

class APIInterface:
    """API 인터페이스 관리 클래스"""
    def __init__(self, api_type: str, environment: str):
        self.api_type = api_type
        self.environment = environment
        self.api = self._initialize_api()
    
    def _initialize_api(self):
        """API 타입에 따른 인터페이스 초기화"""
        if self.api_type == "OpenAI GPT-4":
            return OpenAIInterface()
        else:
            return GroqInterface()
    
    def generate_strategy(self, market_data):
        """선택된 API로 전략 생성"""
        return self.api.generate_strategy(market_data) 