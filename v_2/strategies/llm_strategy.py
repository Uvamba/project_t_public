"""
LLM 기반 거래 전략 클래스
LLM의 분석을 실제 거래 신호로 변환하고 실행

# 주요 기능:
- LLM 분석 요청
  - 시장 데이터 전처리
  - 프롬프트 생성
  - 응답 처리

- 거래 신호 생성
  - 텍스트 분석
  - 매매 시그널 추출
  - 거래량 결정

- 리스크 관리
  - 포지션 크기 제한
  - 손실 제한
  - 수익 실현
"""
from models.llm_interface import LLMInterface
from models.strategy_generator import StrategyGenerator

class LLMStrategy:
    def __init__(self, api_key, client):
        """
        LLM 기반 전략 초기화
        
        Args:
            api_key (str): LLM API 키
            client: 바이낸스 클라이언트 인스턴스
            
        Features:
            - LLM 인터페이스 초기화
            - 전략 생성기 설정
            - 거래 클라이언트 연결
        """
        self.llm = LLMInterface(api_key)
        self.generator = StrategyGenerator()
        self.client = client

    def execute(self, market_data):
        """
        시장 데이터 분석 및 거래 실행
        
        Process:
        1. 시장 데이터 LLM 분석 요청
        2. 분석 결과를 거래 신호로 변환
        3. 거래 실행 및 모니터링
        
        Args:
            market_data (dict): 현재 시장 데이터
                - price: 현재가
                - volume: 거래량
                - bid/ask: 호가 정보
                
        Returns:
            dict: 실행된 주문 정보 또는 None
        """
        # LLM에게 전략 요청
        llm_output = self.llm.generate_strategy(market_data)
        
        # 전략을 실행 가능한 형태로 변환
        strategy = self.generator.parse_strategy(llm_output)

        # 매매 신호에 따른 주문 실행
        if strategy["action"] == "buy":
            print(f"매수 실행: {strategy['amount']} BTC")
            return self.client.place_order('BTC/USDT', 'buy', strategy['amount'])
        elif strategy["action"] == "sell":
            print(f"매도 실행: {strategy['amount']} BTC")
            return self.client.place_order('BTC/USDT', 'sell', strategy['amount'])
        return None 