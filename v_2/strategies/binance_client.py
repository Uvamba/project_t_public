"""
바이낸스 거래소 API 클라이언트
실제 거래 실행과 포지션 관리를 담당

# 주요 기능:
- 계정 관리
  - 잔고 조회
  - 포지션 정보
  - 거래 내역
  
- 주문 실행
  - 시장가 주문
  - 지정가 주문
  - 주문 취소
  
- 시장 데이터
  - 실시간 가격
  - 오더북 정보
  - OHLCV 데이터
  
- 리스크 관리
  - 포지션 제한
  - 손절/익절
  - 레버리지 설정
"""

import ccxt
import pandas as pd
from typing import Dict, Any
from datetime import datetime

class BinanceClient:
    def __init__(self, api_key: str = '', secret_key: str = '', testnet: bool = True):
        """
        바이낸스 클라이언트 초기화
        """
        # 테스트넷 URL 설정
        urls = {
            'api': {
                'public': 'https://testnet.binance.vision/api/v3',
                'private': 'https://testnet.binance.vision/api/v3',
                'v1': 'https://testnet.binance.vision/api/v1',
                'v3': 'https://testnet.binance.vision/api/v3',
            }
        } if testnet else None
        
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True,
                'testnet': testnet,
                'urls': urls
            }
        })
        
        self.exchange.load_markets()  # 거래 가능한 마켓 정보 로드
        self.trade_history = []  # 거래 내역 저장

    def get_market_price(self, symbol: str) -> float:
        """현재가 조회"""
        ticker = self.exchange.fetch_ticker(symbol)
        return ticker['last']
    
    def get_balance(self) -> Dict[str, Any]:
        """계정 잔고 조회"""
        return self.exchange.fetch_balance()
    
    def place_order(self, symbol: str, side: str, amount: float, price: float = None):
        """
        주문 실행
        
        Args:
            symbol (str): 거래쌍 (예: 'BTC/USDT')
            side (str): 매수/매도 ('buy' 또는 'sell')
            amount (float): 거래량
            price (float, optional): 지정가 주문 시 가격
        """
        try:
            order = self.exchange.create_limit_order(symbol, side, amount, price)
            
            # 거래 내역 저장
            self.trade_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price or self.get_market_price(symbol),
                'status': order['status']
            })
            return order
        except Exception as e:
            raise e

    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100):
        """
        OHLCV 데이터 조회
        
        Args:
            symbol (str): 거래 페어
            timeframe (str): 시간단위
            limit (int): 데이터 개수
            
        Returns:
            list: [[timestamp, open, high, low, close, volume], ...]
        """
        return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    def get_orderbook(self, symbol: str):
        """호가창 정보 조회"""
        return self.exchange.fetch_order_book(symbol)

    def get_position(self, symbol: str):
        """
        현재 포지션 정보 조회
        
        Args:
            symbol (str): 거래 페어 (예: 'BTC/USDT')
            
        Returns:
            dict: {
                'base': {'free': BTC잔고, 'used': 사용중, 'total': 전체},
                'quote': {'free': USDT잔고, 'used': 사용중, 'total': 전체}
            }
        """
        balance = self.exchange.fetch_balance()
        base, quote = symbol.split('/')
        
        return {
            'base': balance[base],
            'quote': balance[quote]
        }

    def get_trade_stats(self):
        """
        거래 통계 정보
        
        Returns:
            dict: {
                'total_trades': 총 거래 횟수,
                'success_rate': 성공률,
                'total_volume': 총 거래대금,
                'avg_trade_size': 평균 거래량
            }
        """
        # TODO: 실제 거래 통계 구현
        return {
            'total_trades': 0,
            'buy_trades': 0,
            'sell_trades': 0,
            'success_rate': 0.0,
            'total_volume': 0.0,
            'avg_trade_size': 0.0
        } 