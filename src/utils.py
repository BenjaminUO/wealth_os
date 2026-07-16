"""
WEALTH OS - CORE UTILITY ENGINE
Provides centralized, rate-limited network requests, caching,
ticker translations, and strict historical/live FX calculations.
"""

import pandas as pd
import yfinance as yf
import requests as std_requests
from curl_cffi import requests as cffi_requests
import time
from functools import lru_cache
from typing import Optional, Tuple

# Import the Master Configurations
from src.config import EXCHANGE_SUFFIX_MAP, FALLBACK_FX_RATES

# ==========================================
# 1. TICKER & EXCHANGE TRANSLATION ENGINE
# ==========================================

def google_to_yahoo(gf_ticker: str) -> Optional[str]:
    """
    Translates Google Finance ticker prefixes (STO:) back to Yahoo suffixes (.ST).
    Ensures safe evaluation for Python backend processing.
    """
    if not gf_ticker or pd.isna(gf_ticker) or gf_ticker == "N/A":
        return None
        
    if ":" in str(gf_ticker):
        exchange, symbol = gf_ticker.split(":", 1)
        # Reverse the lookup map
        suffix = EXCHANGE_SUFFIX_MAP.get(exchange.upper(), "")
        return f"{symbol}{suffix}"
        
    return gf_ticker


@lru_cache(maxsize=500)
def get_yf_currency(yf_ticker: str) -> Tuple[str, float]:
    """
    Fast-path currency extractor. Prevents API bans by using known logic
    before pinging the Yahoo servers. Fixes the London ETF USD bug.
    Returns: (currency_code, price_multiplier)
    """
    if not yf_ticker or yf_ticker == "N/A":
        return "SEK", 1.0
        
    # 1. THE LONDON ETF USD SHIELD (Bypass LSE Pence assumption)
    USD_LSE_ETFS = ['VUAA.L', 'SPYL.L', 'CSPX.L', 'IUIT.L', 'VWRA.L', 'VUSD.L', 'CNX1.L', 'XDWT.L', 'IB01.L']
    if yf_ticker in USD_LSE_ETFS:
        return "USD", 1.0

    # 2. SPECIAL EXCEPTIONS FOR STOCKHOLM TICKERS
    if yf_ticker == 'VSURE.ST':
        return "EUR", 1.0

    # 3. FAST-PATH EXCHANGES (Bypasses the API entirely, prevents rate limits!)
    if yf_ticker.endswith('.ST'): return "SEK", 1.0
    if yf_ticker.endswith(('.DE', '.PA', '.AS', '.MC', '.IR', '.HE', '.VI')): return "EUR", 1.0
    if yf_ticker.endswith('.CO'): return "DKK", 1.0
    if yf_ticker.endswith('.OL'): return "NOK", 1.0
    if yf_ticker.endswith(('.TO', '.V')): return "CAD", 1.0
    if yf_ticker.endswith('.SW'): return "CHF", 1.0
    
    # Standard US Stocks (like HOOD, AAPL, AMZN) have no dot suffix
    if "." not in yf_ticker:
        return "USD", 1.0
        
    # 3. Active Ping for remaining unknowns (Mostly edge-case LSE stocks)
    try:
        info = yf.Ticker(yf_ticker).fast_info
        currency = getattr(info, 'currency', None)
        
        if currency:
            if currency == "GBp": return "GBP", 0.01
            elif currency == "Zp": return "ZAR", 0.01
            elif currency == "ILp": return "ILS", 0.01
            else: return currency.upper(), 1.0
    except Exception:
        pass
        
    # 4. Ultimate Fallback if network drops
    if yf_ticker.endswith('.L'): return "GBP", 0.01
    return "USD", 1.0


# ==========================================
# 2. ROBUST NETWORK OPERATIONS
# ==========================================

import random # Add this to your imports at the top

def robust_get(url: str, use_cffi: bool = False, max_retries: int = 3, headers: dict = None) -> Optional[std_requests.Response]:
    if headers is None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    for attempt in range(1, max_retries + 1):
        try:
            if use_cffi:
                res = cffi_requests.get(url, headers=headers, impersonate="chrome", timeout=10)
            else:
                res = std_requests.get(url, headers=headers, timeout=10)
            
            if res.status_code == 200:
                return res
            elif res.status_code == 429:
                # Exponential Backoff with Jitter (e.g., 2s, 4s, 8s + random milliseconds)
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"   API Throttled (429). Exponential backoff for {sleep_time:.2f}s...")
                time.sleep(sleep_time)
            else:
                return res
                
        except Exception as e:
            if attempt == max_retries:
                print(f" ❌ Network failure on {url}: {e}")
                return None
            time.sleep(attempt)
            
    return None


# ==========================================
# 3. CURRENCY & FX PHYSICS ENGINE
# ==========================================

@lru_cache(maxsize=32)
def get_live_fx_rate(currency: str) -> Tuple[float, float]:
    """
    Fetches the live exchange rate with a 5-day backward buffer.
    Returns a tuple: (fx_rate, price_multiplier) to handle the British Pence anomaly.
    @lru_cache ensures we only ping Yahoo ONCE per currency per execution run.
    """
    safe_currency = currency.strip()
    multiplier = 1.0
    
    # Handle the Yahoo Pence (GBp) anomaly natively
    if safe_currency == "GBp":
        safe_currency = "GBP"
        multiplier = 0.01
        
    safe_currency = safe_currency.upper()
    
    if safe_currency in ["SEK", "N/A", ""]:
        return 1.0, multiplier
        
    # Explicitly handle Yahoo's USD formatting
    pair = "SEK=X" if safe_currency == "USD" else f"{safe_currency}SEK=X"
    
    try:
        # Step 1: Attempt fast_info for instant sub-millisecond retrieval
        rate = yf.Ticker(pair).fast_info.last_price
        if rate is not None and rate > 0:
            return float(rate), multiplier
            
        # Step 2: Attempt standard history retrieval
        hist = yf.Ticker(pair).history(period="5d")
        if not hist.empty and 'Close' in hist.columns:
            # THE DELISTED SHIELD: Prevents IndexError if Yahoo returns an empty array
            clean_s = hist['Close'].ffill().dropna()
            if not clean_s.empty:
                return float(clean_s.iloc[-1]), multiplier
                
    except Exception as e:
        print(f" ⚠️ FX API Warning for {pair}: {e}. Falling back to hardcoded safety rates.")
        
    # Step 3: Absolute fail-safe to prevent pipeline crash
    return FALLBACK_FX_RATES.get(safe_currency, 1.0), multiplier


def get_historical_fx_rate(currency: str, target_date: pd.Timestamp) -> Tuple[float, float]:
    """
    THE BULLETPROOF FIX: Safely fetches the exact historical FX rate for a specific date.
    Returns a tuple: (fx_rate, price_multiplier).
    If the date lands on a weekend/holiday, it looks backward up to 7 days to find the last close.
    """
    safe_currency = currency.strip()
    multiplier = 1.0
    
    if safe_currency == "GBp":
        safe_currency = "GBP"
        multiplier = 0.01
        
    safe_currency = safe_currency.upper()
    
    if safe_currency in ["SEK", "N/A", ""]:
        return 1.0, multiplier
        
    pair = "SEK=X" if safe_currency == "USD" else f"{safe_currency}SEK=X"
    
    # We buffer the end date by 1 day because yfinance history 'end' is exclusive
    start_str = (target_date - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
    end_str = (target_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')

    try:
        # Fetch a 7-day window ending on the target date
        fx_data = yf.Ticker(pair).history(start=start_str, end=end_str)
        
        if not fx_data.empty and 'Close' in fx_data.columns:
            # --- THE TIMEZONE POISONING SHIELD ---
            # Yahoo often returns tz-aware indexes which crash against our tz-naive target_date
            if fx_data.index.tz is not None:
                fx_data.index = fx_data.index.tz_localize(None)
            fx_data.index = fx_data.index.normalize()

            # .asof() guarantees we get the exact date, or the closest prior date (e.g. Friday for a Sunday)
            valid_rate = fx_data['Close'].asof(target_date)
            if pd.notna(valid_rate):
                return float(valid_rate), multiplier
                
    except Exception as e:
        print(f" ⚠️ Historical FX API Failure for {pair} on {target_date.strftime('%Y-%m-%d')}: {e}")

    # --- THE STRICT HISTORICAL FALLBACK ---
    print(f" 🛑 CRITICAL: Using static config fallback for {pair} on {target_date.strftime('%Y-%m-%d')} to prevent historical math corruption.")
    return FALLBACK_FX_RATES.get(safe_currency, 1.0), multiplier


# ==========================================
# 4. STRING & DATA NORMALIZATION
# ==========================================

def clean_swedish_numbers(series: pd.Series) -> pd.Series:
    r"""
    Vectorized cleaning of Swedish number formats into Python calculable floats.
    Uses raw string regex r'\s+' to absolutely annihilate ANY kind of space.
    """
    return series.astype(str)\
                 .str.replace(r'\s+', '', regex=True)\
                 .str.replace(',', '.', regex=False)\
                 .replace(['nan', 'None', ''], '0.0')\
                 .astype(float)