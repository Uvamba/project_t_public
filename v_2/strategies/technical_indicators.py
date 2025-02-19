import pandas as pd
import ta
import pandas_ta as pta
from typing import Dict, Any

class TechnicalAnalysis:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        
    def analyze_rsi_macd(self, timeframe: str = '1h') -> Dict[str, Any]:
        """
        RSI와 MACD 기반의 실용적인 매매 시그널 분석
        
        Args:
            timeframe: 분석 시간단위 (1h, 4h, 1d 등)
            
        Returns:
            Dict: 분석 결과 및 매매 시그널
        """
        # 기존 지표 계산
        self.add_rsi()
        self.add_macd()
        
        # 현재 값들
        current_rsi = self.df['RSI'].iloc[-1]
        current_macd = self.df['MACD'].iloc[-1]
        current_signal = self.df['MACD_Signal'].iloc[-1]
        current_hist = self.df['MACD_Hist'].iloc[-1]
        
        # 시그널 생성
        signals = []
        
        # RSI 시그널
        if current_rsi < 30:
            signals.append({
                'indicator': 'RSI',
                'signal': '과매도',
                'strength': 'strong',
                'action': 'consider_buy'
            })
        elif current_rsi > 70:
            signals.append({
                'indicator': 'RSI',
                'signal': '과매수',
                'strength': 'strong',
                'action': 'consider_sell'
            })
            
        # MACD 시그널
        if current_hist > 0 and current_macd > current_signal:
            signals.append({
                'indicator': 'MACD',
                'signal': '상승추세',
                'strength': 'medium',
                'action': 'consider_buy'
            })
        elif current_hist < 0 and current_macd < current_signal:
            signals.append({
                'indicator': 'MACD',
                'signal': '하락추세',
                'strength': 'medium',
                'action': 'consider_sell'
            })
            
        return {
            'timestamp': self.df.index[-1],
            'current_price': self.df['close'].iloc[-1],
            'rsi': current_rsi,
            'macd': current_macd,
            'macd_signal': current_signal,
            'macd_hist': current_hist,
            'signals': signals,
            'trend': self._analyze_trend(),
            'historical_data': self.df  # 시각화를 위한 전체 데이터 추가
        }
    
    def _analyze_trend(self) -> Dict[str, str]:
        """
        RSI와 MACD를 종합적으로 평가하여 트렌드 강도 판단
        """
        trend = {
            'direction': 'neutral',
            'strength': 'weak',
            'description': ''
        }
        
        # RSI 트렌드 판단
        if self.df['RSI'].iloc[-1] > 60:
            trend['direction'] = 'bullish'
        elif self.df['RSI'].iloc[-1] < 40:
            trend['direction'] = 'bearish'
            
        # MACD 히스토그램으로 트렌드 강도 보강
        if abs(self.df['MACD_Hist'].iloc[-1]) > 0.5 * self.df['MACD_Signal'].iloc[-1]:
            trend['strength'] = 'strong'
        
        trend['description'] = f"{trend['strength']} {trend['direction']} trend"
        
        return trend

    def add_all_indicators(self):
        # 추세 지표
        self.add_moving_averages()
        self.add_macd()
        
        # 모멘텀 지표
        self.add_rsi()
        self.add_stochastic()
        
        # 변동성 지표
        self.add_bollinger_bands()
        self.add_atr()
        
        return self.df
    
    def add_moving_averages(self):
        self.df['SMA_20'] = ta.trend.sma_indicator(self.df['close'], window=20)
        self.df['EMA_20'] = ta.trend.ema_indicator(self.df['close'], window=20)
        
    def add_rsi(self, period: int = 14):
        """RSI 지표 추가"""
        self.df['RSI'] = ta.momentum.rsi(self.df['close'], window=period)
        
    def add_macd(self, fast: int = 12, slow: int = 26, signal: int = 9):
        """MACD 지표 추가"""
        macd = ta.trend.MACD(
            self.df['close'],
            window_fast=fast,
            window_slow=slow,
            window_sign=signal
        )
        self.df['MACD'] = macd.macd()
        self.df['MACD_Signal'] = macd.macd_signal()
        self.df['MACD_Hist'] = macd.macd_diff()
        
    def add_stochastic(self):
        stoch = ta.momentum.StochasticOscillator(
            self.df['high'], 
            self.df['low'], 
            self.df['close']
        )
        self.df['Stoch_K'] = stoch.stoch()
        self.df['Stoch_D'] = stoch.stoch_signal()
        
    def add_bollinger_bands(self):
        bb = ta.volatility.BollingerBands(self.df['close'])
        self.df['BB_Upper'] = bb.bollinger_hband()
        self.df['BB_Lower'] = bb.bollinger_lband()
        
    def add_atr(self):
        self.df['ATR'] = ta.volatility.average_true_range(
            self.df['high'], 
            self.df['low'], 
            self.df['close']
        ) 