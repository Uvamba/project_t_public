"""
LLM 기반 거래 전략 클래스
기술적 분석과 LLM의 분석을 결합하여 최종 매매 결정

주요 기능:
1. 시장 데이터 분석
2. 매매 신호 검증
3. 거래 실행 결정
4. 리스크 관리
"""
from models.llm_interface import LLMAnalyzer
from models.strategy_generator import StrategyGenerator
from .technical_indicators import TechnicalAnalysis

class LLMStrategy:
    def __init__(self, api_key: str, client, llm_provider: str = "groq"):
        """
        LLM 전략 초기화
        
        Args:
            api_key: LLM API 키
            client: 거래소 클라이언트
            llm_provider: 사용할 LLM 제공자
        """
        self.api_key = api_key
        self.analyzer = LLMAnalyzer(api_key, provider=llm_provider)
        self.generator = StrategyGenerator()
        self.client = client
        self.technical_analysis = None

    def analyze_market(self, market_data):
        """
        시장 데이터 종합 분석
        
        Args:
            market_data (pd.DataFrame): OHLCV 데이터
            
        Returns:
            Dict: {
                'llm_analysis': str,      # LLM 분석 결과
                'technical_analysis': Dict,  # 기술적 분석 결과
                'chart_data': pd.DataFrame  # 차트 데이터
            }
        """
        # 기술적 분석 수행
        self.technical_analysis = TechnicalAnalysis(market_data)
        analysis_result = self.technical_analysis.analyze_rsi_macd()
        
        # LLM 분석 요청
        prompt = self.analyzer.generate_analysis_prompt(
            market_data=market_data,
            analysis_result=analysis_result
        )
        
        # LLM 응답 처리
        analysis = self.analyzer.get_analysis(prompt)
        
        # 분석 결과와 차트 데이터 함께 반환
        return {
            'llm_analysis': analysis,
            'technical_analysis': analysis_result,
            'chart_data': analysis_result['historical_data']
        }

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
        # 시장 분석 수행
        analysis_result = self.analyze_market(market_data)
        
        # 전략 생성
        strategy = self.generator.parse_strategy(analysis_result['llm_analysis'])
        
        # 기술적 시그널과 LLM 분석이 일치하는지 검증
        if not self._validate_signals(strategy, analysis_result['technical_analysis']):
            print("기술적 시그널과 LLM 분석이 일치하지 않아 매매 보류")
            return None

        # 매매 신호에 따른 주문 실행
        if strategy["action"] == "buy":
            print(f"매수 실행: {strategy['amount']} BTC")
            return self.client.place_order('BTC/USDT', 'buy', strategy['amount'])
        elif strategy["action"] == "sell":
            print(f"매도 실행: {strategy['amount']} BTC")
            return self.client.place_order('BTC/USDT', 'sell', strategy['amount'])
        return None

    def _validate_signals(self, strategy, technical_signals):
        """
        LLM 전략과 기술적 시그널의 일치성 검증
        """
        # 기술적 시그널이 없으면 LLM 판단만으로 진행
        if not technical_signals['signals']:
            return True
            
        # 매수 시그널 검증
        if strategy['action'] == 'buy':
            return any(s['action'] == 'consider_buy' for s in technical_signals['signals'])
            
        # 매도 시그널 검증
        if strategy['action'] == 'sell':
            return any(s['action'] == 'consider_sell' for s in technical_signals['signals'])
            
        return False 