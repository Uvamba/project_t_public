"""
환경변수 기반 설정 관리
"""
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """
    환경변수에서 설정 로드
    로컬 개발 시에는 config.yaml 사용
    """
    # 로컬 개발 환경 확인
    if os.getenv('ENVIRONMENT') == 'development':
        import yaml
        with open('utils/config.yaml', 'r') as file:
            return yaml.safe_load(file)
            
    # Heroku 환경용 설정
    return {
        'binance': {
            'live': {
                'api_key': os.getenv('BINANCE_LIVE_API_KEY', ''),
                'secret_key': os.getenv('BINANCE_LIVE_SECRET_KEY', '')
            },
            'testnet': {
                'api_key': os.getenv('BINANCE_TEST_API_KEY', ''),
                'secret_key': os.getenv('BINANCE_TEST_SECRET_KEY', '')
            }
        },
        'groq': {
            'api_key': os.getenv('GROQ_API_KEY', ''),
            'model': os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
        },
        'trading': {
            'interval': int(os.getenv('TRADING_INTERVAL', '300')),
            'max_amount': float(os.getenv('MAX_AMOUNT', '1.0')),
            'min_amount': float(os.getenv('MIN_AMOUNT', '0.001')),
            'symbol': os.getenv('TRADING_SYMBOL', 'BTC/USDT')
        }
    }