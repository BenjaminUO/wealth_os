"""
WEALTH OS - MARKET DATA MAPPER
Translates local Swedish broker assets into global financial tickers,
and directly scrapes live Net Asset Values (NAV) for unlisted mutual funds.
"""

import pandas as pd
import json
import time
import urllib.parse
import re
import yfinance as yf
from typing import Tuple, Optional, Dict, Any

# Import Master Configurations and Utilities
from src.config import (
    TRANSACTIONS_FILE, MAPPING_FILE, MANUAL_TICKER_OVERRIDES,
    DIRECT_FUND_IDS, KNOWN_YAHOO_TICKERS, EXCHANGE_SUFFIX_MAP,
    PROCESSED_DIR  # <-- NEW: Added this
)
from src.utils import robust_get, get_yf_currency


# ==========================================
# 1. HELPER FUNCTIONS & TRANSLATORS
# ==========================================

def yahoo_to_google(yf_ticker: str, quote_type: str) -> str:
    """
    Translates a Yahoo suffix (e.g., .ST) into a Google Finance prefix (e.g., STO:).
    Rejects Mutual Funds and Crypto so the backend NAV scraper can handle them natively.
    """
    if quote_type == "MUTUALFUND": return "REJECTED_MUTUALFUND"
    if quote_type == "CRYPTOCURRENCY": return "REJECTED_CRYPTO"

    if "." not in yf_ticker:
        return yf_ticker.replace("-", ".")

    # Split at the last dot to isolate the exchange suffix
    base, suffix = yf_ticker.rsplit(".", 1)

    # Invert the config map: {".ST": "STO", ".CO": "CPH", ...}
    inverse_map = {v.replace(".", ""): k for k, v in EXCHANGE_SUFFIX_MAP.items()}

    if suffix in ["ST", "CO", "HE", "OL"]:
        base = base.replace(" ", "-")

    if suffix in inverse_map:
        return f"{inverse_map[suffix]}:{base}"

    return yf_ticker


def sanitize_fund_name(name: str) -> str:
    """Strips junk artifacts from broker fund names to improve search hit rates."""
    clean = re.sub(r'\(.*?\)', '', name)
    junk_suffixes = [
        ' C/R', ' A2', ' BY SKOGLUND', ' D-EUR CAP', ' A USD', 
        ' C USD C', ' A', ' B', ' GROUP', ' AB', ' CORP', ' PLC', ' INC'
    ]
    for suffix in junk_suffixes:
        if clean.endswith(suffix): 
            clean = clean[:-len(suffix)]
    return clean.strip()


# ==========================================
# 2. PHASE 1: TICKER DISCOVERY ENGINE
# ==========================================

def search_yahoo_api(query_string: str, is_swedish: bool = False) -> Tuple[str, str]:
    """Queries Yahoo Finance for a ticker symbol, prioritizing local exchanges if needed."""
    if not query_string or pd.isna(query_string): 
        return "N/A", "Empty Query"

    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(str(query_string))}&quotesCount=5"
    
    res = robust_get(url, use_cffi=False)
    if not res:
        return "N/A", "API Error / Timeout"

    try:
        data = res.json()
        if data.get("quotes") and len(data["quotes"]) > 0:
            # Filter out cryptocurrency pollution
            valid_quotes = [q for q in data["quotes"] if q.get("quoteType") != "CRYPTOCURRENCY"]
            if not valid_quotes: 
                return "N/A", "Rejected: Crypto Match"

            best_quote = valid_quotes[0]

            # If it's a Swedish ISIN, force the search to prioritize the Stockholm exchange
            if is_swedish:
                for q in valid_quotes:
                    exch = q.get("exchange", "")
                    sym = str(q.get("symbol", ""))
                    if exch in ["STO", "NGM"] or sym.endswith(".ST"):
                        best_quote = q
                        break

            symbol = best_quote.get("symbol", "")
            q_type = best_quote.get("quoteType", "EQUITY")
            
            return yahoo_to_google(symbol, q_type), q_type
            
    except Exception as e:
        return "N/A", f"JSON Parse Error: {str(e)}"
        
    return "N/A", "No Results Found"


def generate_ticker_mapping():
    """Reads transactions, finds unmapped assets, and discovers their global tickers."""
    if not TRANSACTIONS_FILE.exists():
        print(f"🚨 Missing {TRANSACTIONS_FILE.name}. Run cleaner.py first.")
        return

    df = pd.read_csv(TRANSACTIONS_FILE)
    
    # Map every unique asset to its last known ISIN
    asset_isin_map = df[df['ISIN'].notna() & (df['ISIN'] != '')].groupby('Asset')['ISIN'].last().to_dict()
    unique_assets = df['Asset'].dropna().unique().tolist()

    mapping = {}
    if MAPPING_FILE.exists():
        with open(MAPPING_FILE, "r", encoding='utf-8') as f:
            mapping = json.load(f)

    # Purge broken or temporary mappings to force a retry
    for asset, data in list(mapping.items()):
        if asset in MANUAL_TICKER_OVERRIDES:
            continue
        t = data.get("ticker", "")
        if t == "N/A" or t == "QNT" or "USD" in t:
            del mapping[asset]

    new_assets = [asset for asset in unique_assets if asset not in mapping]

    if not new_assets:
        print("✅ All assets are mapped! Ready to scrape live NAVs.")
        return

    print(f"\n📡 Booting up Diagnostic ISIN Engine for {len(new_assets)} missing assets...")

    for i, asset in enumerate(new_assets):
        isin = str(asset_isin_map.get(asset, "")).strip()
        reason = ""
        ticker = "N/A"
        clean_asset_key = asset.strip().upper()

        # Step 1: Check Master Config Overrides
        if clean_asset_key in MANUAL_TICKER_OVERRIDES:
            ticker = MANUAL_TICKER_OVERRIDES[clean_asset_key]
            reason = "Success: Config Manual Override"
            
        else:
            is_swe = isin.startswith("SE")

            # Step 2: Search via Official ISIN
            if isin:
                ticker, q_type = search_yahoo_api(isin, is_swe)
                if ticker == "REJECTED_MUTUALFUND": ticker, reason = "N/A", "Rejected: Mutual Fund"
                elif ticker == "REJECTED_CRYPTO": ticker, reason = "N/A", "Rejected: Crypto"
                elif ticker != "N/A": reason = f"Success: Found via ISIN ({q_type})"

            # Step 3: Fallback Search via Cleaned Asset Name
            if ticker == "N/A" and "Rejected" not in reason:
                clean_name = sanitize_fund_name(asset)
                ticker, q_type = search_yahoo_api(clean_name)
                
                if ticker == "REJECTED_MUTUALFUND": ticker, reason = "N/A", "Rejected: Mutual Fund"
                elif ticker == "REJECTED_CRYPTO": ticker, reason = "N/A", "Rejected: Crypto"
                elif ticker != "N/A": reason = f"Success: Found via Name Fallback ({q_type})"
                else: reason = "Failed: No Yahoo Match"

        print(f"   [{i+1}/{len(new_assets)}] {asset} -> Ticker: {ticker} | {reason}")
        mapping[asset] = {"isin": isin, "ticker": ticker, "fallback_price": None, "diagnostic": reason}

        # Incremental save to protect against unexpected crashes
        if (i+1) % 5 == 0:
            with open(MAPPING_FILE, "w", encoding='utf-8') as f:
                json.dump(mapping, f, indent=4)
            time.sleep(0.5) # Prevent Yahoo throttling

    # Final Save
    with open(MAPPING_FILE, "w", encoding='utf-8') as f:
        json.dump(mapping, f, indent=4)
    print("🎯 Mapping complete! Assets rejected as Mutual Funds will now be handled by the NAV scraper.")


# ==========================================
# 3. PHASE 2: LIVE NAV SCRAPING ENGINE
# ==========================================

def fetch_avanza_direct_fund(asset_name: str) -> Tuple[Optional[float], str]:
    """Scrapes Avanza's backend API using direct fund IDs from config."""
    if asset_name in DIRECT_FUND_IDS:
        url = f"https://www.avanza.se/_api/fund-guide/guide/{DIRECT_FUND_IDS[asset_name]}"
        res = robust_get(url, use_cffi=True) # Needs cffi to bypass Cloudflare
        
        if res and res.status_code == 200:
            data = res.json()
            price = data.get("nav") or data.get("lastPrice")
            if price: 
                return float(price), data.get("currency", "SEK")
    return None, "SEK"

def fetch_historical_avanza_nav(asset_name: str, fund_id: str) -> pd.DataFrame:
    """
    Scrapes Avanza's chart API to get the full historical price curve of a mutual fund.
    Returns a DataFrame formatted exactly like yfinance historical data.
    """
    print(f"   -> Fetching historical time-series for {asset_name}...")
    
    # Avanza's hidden chart endpoint (MAX retrieves all available history)
    url = f"https://www.avanza.se/_api/fund-guide/chart/{fund_id}/MAX"
    
    res = robust_get(url, use_cffi=True)
    if not res or res.status_code != 200:
        print(f"      ❌ Failed to fetch history for {asset_name}")
        return pd.DataFrame()

    data = res.json()
    
    # The API returns a list of data series. We want the one labeled 'NAV'
    nav_series = next((series for series in data.get('dataSeries', []) if series.get('type') == 'NAV'), None)
    
    if not nav_series or not nav_series.get('data'):
        return pd.DataFrame()

    # Avanza returns data as: [unix_timestamp_milliseconds, price]
    df = pd.DataFrame(nav_series['data'], columns=['timestamp', asset_name])
    
    # Convert Unix timestamps to normalized Pandas Dates
    df['Date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.normalize()
    df = df.drop(columns=['timestamp'])
    df = df.set_index('Date')
    
    print(f"      ✅ Downloaded {len(df)} days of historical data.")
    return df


def fetch_known_ticker(asset_name: str) -> Tuple[Optional[float], str]:
    """Bypasses search API by directly fetching a hardcoded known Yahoo ticker."""
    if asset_name in KNOWN_YAHOO_TICKERS:
        symbol = KNOWN_YAHOO_TICKERS[asset_name]
        t = yf.Ticker(symbol)
        
        try:
            info = t.fast_info
            if getattr(info, 'last_price', None) and info.last_price > 0:
                curr, mult = get_yf_currency(symbol)
                return float(info.last_price) * mult, curr
        except Exception:
            pass
            
        try:
            # THE DELISTED SHIELD: dropna() prevents IndexError if the 5d array returns completely blank
            hist = t.history(period="5d")
            if not hist.empty and 'Close' in hist.columns:
                clean_series = hist['Close'].ffill().dropna()
                if not clean_series.empty:
                    price = float(clean_series.iloc[-1])
                    curr, mult = get_yf_currency(symbol)
                    return price * mult, curr
        except Exception:
            pass
            
    return None, "SEK"


def fetch_nordnet_search(query: str) -> Tuple[Optional[float], str]:
    """Scrapes Nordnet's backend instrument search."""
    url = f"https://www.nordnet.se/api/2/instruments?query={urllib.parse.quote(query)}"
    headers = {'client-id': 'NEXT', 'User-Agent': 'Mozilla/5.0'}
    
    res = robust_get(url, use_cffi=False, headers=headers)
    if res and res.status_code == 200:
        data = res.json()
        if len(data) > 0:
            hit = data[0]
            price = hit.get('last_price') or hit.get('nav')
            if price is not None: 
                return float(price), hit.get("currency", "SEK")
    return None, "SEK"


def fetch_avanza_search(query: str) -> Tuple[Optional[float], str]:
    """Scrapes Avanza's global search endpoint."""
    url = f"https://www.avanza.se/_api/search/global-search?query={urllib.parse.quote(query)}"
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    
    res = robust_get(url, use_cffi=True, headers=headers)
    if res and res.status_code == 200:
        data = res.json()
        for group in data.get("resultGroups", []):
            for hit in group.get("searchHits", []):
                inst = hit.get("instrument", hit)
                for key in ["nav", "lastPrice", "sellPrice", "buyPrice"]:
                    if inst.get(key) is not None:
                        return float(inst[key]), inst.get("currency", "SEK")
    return None, "SEK"


def fetch_yahoo_search_nav(query: str) -> Tuple[Optional[float], str]:
    """Safe fallback to Yahoo Finance for obscure funds using fast_info or history."""
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(query)}&quotesCount=1"
    
    res = robust_get(url, use_cffi=False)
    if res and res.status_code == 200:
        data = res.json()
        if data.get('quotes'):
            symbol = data['quotes'][0]['symbol']
            t = yf.Ticker(symbol)
            
            try:
                info = t.fast_info
                if getattr(info, 'last_price', None) and info.last_price > 0:
                    curr, mult = get_yf_currency(symbol)
                    return float(info.last_price) * mult, curr
            except Exception:
                pass
                
            # THE DELISTED SHIELD: dropna() prevents IndexError if the 5d array returns completely blank
            try:
                hist = t.history(period="5d")
                if not hist.empty and 'Close' in hist.columns:
                    clean_series = hist['Close'].ffill().dropna()
                    if not clean_series.empty:
                        price = float(clean_series.iloc[-1])
                        curr, mult = get_yf_currency(symbol)
                        return price * mult, curr
            except Exception:
                pass
                
    return None, "SEK"


def update_missing_prices():
    """Iterates through all unlisted assets and scrapes their live market values."""
    if not MAPPING_FILE.exists():
        print(f"🚨 Missing {MAPPING_FILE.name}. Run mapping generator first.")
        return

    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    updated_count = 0
    print("\n🌐 Initiating Live NAV Scraping for Unlisted Assets...")

    for asset, data in mapping.items():
        ticker = data.get("ticker", "N/A")
        fallback_price = data.get("fallback_price")
        isin = data.get("isin", "")

        # Only scrape assets that lack a formal stock ticker
        if ticker == "N/A" and fallback_price != "DELISTED":
            
            # --- THE JUNK ARTIFACT PURGE ---
            # Automatically delist subscription rights, warrants, and artifacts
            junk_keywords = [' TR', ' TO ', ' BTA', ' UR', ' TIA', 'SMS', 'UTBETALNING']
            if any(junk in asset.upper() for junk in junk_keywords):
                mapping[asset]["fallback_price"] = "DELISTED"
                updated_count += 1
                continue

            print(f"   -> Scraping NAV for: {asset}...")
            
            # Strategy A: Config Direct Fund ID (100% accurate)
            live_price, currency = fetch_avanza_direct_fund(asset)
            
            # Strategy B: Known Yahoo Ticker Fallback
            if not live_price:
                live_price, currency = fetch_known_ticker(asset)
            
            # Strategy C: Search string permutations across 3 different APIs
            if not live_price:
                clean_name = sanitize_fund_name(asset)
                queries = []
                if isin: queries.append(isin) 
                
                for q in [asset, clean_name, " ".join(clean_name.split()[:3])]:
                    if q.strip() and q.strip() not in queries: 
                        queries.append(q.strip())

                for q in queries:
                    if live_price: break
                    for fetcher in [fetch_nordnet_search, fetch_avanza_search, fetch_yahoo_search_nav]:
                        live_price, currency = fetcher(q)
                        if live_price: break

            # Save Result
            if live_price:
                print(f"      ✅ Success! {round(live_price, 2)} {currency}")
                mapping[asset]["fallback_price"] = live_price
                mapping[asset]["fallback_currency"] = currency
                updated_count += 1
            else:
                print(f"      ❌ Failed to resolve. Will retry next run.")
                mapping[asset]["fallback_price"] = None
                mapping[asset]["fallback_currency"] = "SEK"

            time.sleep(0.5) # Polite scraping delay

    if updated_count > 0:
        with open(MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=4)
        print(f"\n🎯 NAV Scraping Finished! Updated {updated_count} unlisted assets.")
    else:
        print("\n✅ All non-ticker assets are already up to date.")

# ==========================================
# 4. PHASE 3: HISTORICAL NAV DATABASE
# ==========================================

def build_historical_fund_database():
    """Loops through known mutual funds, downloads their full history, and knits them into a single CSV."""
    print("\n📚 Building Historical Mutual Fund Database...")
    
    if not DIRECT_FUND_IDS:
        print("   No direct fund IDs configured in config.py. Skipping.")
        return

    all_fund_data = []
    
    for asset_name, fund_id in DIRECT_FUND_IDS.items():
        fund_df = fetch_historical_avanza_nav(asset_name, fund_id)
        if not fund_df.empty:
            all_fund_data.append(fund_df)
        time.sleep(1) # Polite pacing to prevent Avanza from blocking your IP
        
    if all_fund_data:
        # Concat horizontally (knitting them side-by-side based on the Date index)
        master_fund_df = pd.concat(all_fund_data, axis=1)
        
        # Forward-fill any internal gaps (e.g. if one fund updated late)
        master_fund_df = master_fund_df.ffill()
        
        output_file = PROCESSED_DIR / "mutual_fund_hist_prices.csv"
        master_fund_df.to_csv(output_file)
        print(f"🎯 Historical fund database saved! ({len(master_fund_df)} days tracked) -> {output_file.name}")
    else:
        print("⚠️ No historical fund data could be aggregated.")

if __name__ == "__main__":
    generate_ticker_mapping()
    update_missing_prices()
    build_historical_fund_database() # <-- NEW: Triggers Phase 3