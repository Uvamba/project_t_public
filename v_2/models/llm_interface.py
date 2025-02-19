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
import groq
import openai

class LLMInterface(ABC):
    @abstractmethod
    def __init__(self, api_key: str):
        """LLM 인터페이스 초기화"""
        self.api_key = api_key

    @abstractmethod
    def get_analysis(self, prompt: str) -> str:
        """LLM에 분석 요청을 보내고 응답을 받음"""
        pass

class GroqLLM(LLMInterface):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = groq.Client(api_key=api_key)
        
    def get_analysis(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "당신은 암호화폐 트레이딩 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return completion.choices[0].message.content

class OpenAILLM(LLMInterface):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = openai.Client(api_key=api_key)
        
    def get_analysis(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 암호화폐 트레이딩 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return completion.choices[0].message.content

class LLMAnalyzer:
    def __init__(self, api_key: str, provider: str = "groq"):
        """
        LLM 분석기 초기화
        
        Args:
            api_key (str): API 키
            provider (str): LLM 제공자 ("groq" 또는 "openai")
        """
        if provider == "groq":
            self.llm = GroqLLM(api_key)
        elif provider == "openai":
            self.llm = OpenAILLM(api_key)
        else:
            raise ValueError(f"지원하지 않는 LLM 제공자: {provider}")
    
    def generate_analysis_prompt(self, market_data, analysis_result):
        prompt = f"""
        현재 비트코인 시장 상황을 분석해주세요:

        시간: {analysis_result['timestamp']}
        현재가: {analysis_result['current_price']}

        핵심 지표:
        1. RSI: {analysis_result['rsi']:.2f}
           - 과매수(70) / 과매도(30) 기준
           - 현재 상태: {self._get_rsi_status(analysis_result['rsi'])}

        2. MACD
           - 현재 MACD: {analysis_result['macd']:.4f}
           - 시그널: {analysis_result['macd_signal']:.4f}
           - 히스토그램: {analysis_result['macd_hist']:.4f}

        감지된 시그널:
        {self._format_signals(analysis_result['signals'])}

        트렌드 평가:
        {analysis_result['trend']['description']}

        위 데이터를 바탕으로:
        1. 현재 시장 상황 요약
        2. 단기 매매 전략 제안 (진입가/손절가 포함)
        3. 리스크 관리 방안
        을 제시해주세요.
        """
        return prompt

    def get_analysis(self, prompt: str) -> str:
        """
        LLM에 분석 요청을 보내고 응답을 받음
        """
        return self.llm.get_analysis(prompt)

    def _get_rsi_status(self, rsi):
        if rsi > 70: return "과매수 구간"
        if rsi < 30: return "과매도 구간"
        return "중립 구간"

    def _format_signals(self, signals):
        if not signals:
            return "현재 특별한 시그널이 감지되지 않았습니다."
        
        return "\n".join([
            f"- {s['indicator']}: {s['signal']} ({s['strength']} signal) -> {s['action']}"
            for s in signals
        ])