"""
트레이딩 화면 컴포넌트
"""

import streamlit as st
from .api_interface import APIInterface

class TradingView:
    def __init__(self, api: APIInterface, environment: str):
        self.api = api
        self.environment = environment
    
    def render(self):
        # 기존의 트레이딩 화면 구현
        # (API 키 설정, 차트, 거래 통계 등)
        pass 