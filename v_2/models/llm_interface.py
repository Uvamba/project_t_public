"""
LLM 기본 인터페이스
모든 LLM 모델의 공통 기능을 정의하는 추상 클래스

# 주요 기능:
- API 통신
  - 요청 처리
  - 응답 파싱
  - 에러 핸들링

- 프롬프트 관리
  - 템플릿 생성
  - 컨텍스트 관리
  - 토큰 제한

- 응답 처리
  - 텍스트 정제
  - 포맷 변환
  - 유효성 검증
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMInterface(ABC):
    def __init__(self, api_key: str):
        """
        LLM 인터페이스 초기화
        
        Args:
            api_key (str): API 인증 키
        """
        self.api_key = api_key
        
    @abstractmethod
    def generate_strategy(self, market_data: Dict[str, Any]) -> str:
        """
        시장 데이터 기반 매매 전략 생성
        
        Args:
            market_data (dict): 현재 시장 데이터
                - price: 현재가
                - volume: 거래량
                - bid: 매수호가
                - ask: 매도호가
                
        Returns:
            str: LLM이 생성한 매매 전략 텍스트
        """
        pass 