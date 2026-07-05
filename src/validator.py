"""
WEALTH OS - OMNISCIENT DETERMINISTIC AUDITOR
Executes a multi-phased forensic sweep across the entire Wealth OS pipeline.
Validates double-entry physics, live ticker connections, portfolio metrics math, 
and historical timeline continuity.
"""

import pandas as pd
import numpy as np
import json
import urllib.parse
import time
from typing import Tuple, Optional, List, Dict, Any

# Import Master Configurations and Utilities
from src.config import (
    PORTFOLIO_FILE, TRANSACTIONS_FILE, MAPPING_FILE, 
    DUPLICATES_FILE, VERIFIED_FILE, METRICS_OUTPUT_FILE,
    HISTORICAL_PERFORMANCE_FILE
)
from src.utils import robust_get

# ==========================================
# 1. NETWORK DIAGNOSTICS & PATCHING
# ==========================================

def is_google_finance_ticker_alive(gf_ticker: str) -> bool:
    """
    Actively pings Google Finance. Simulates a real browser to bypass captchas.
    Returns False if the ticker is 404 Delisted or completely broken.
    """
    if gf_ticker == "N/A" or pd.isna(gf_ticker) or not gf_ticker:
        return False

    if ":" in str(gf_ticker):
        exchange, symbol = gf_ticker.split(":", 1)
        url_ticker = f"{symbol}:{exchange}"
    else:
        url_ticker = f"{gf_ticker}"

    url = f"https://www.google.com/finance/quote/{url_ticker}"
    res = robust_get(url, use_cffi=True, max_retries=2)
    
    if not res: return True # Assume True on total network failure to prevent purges

    if res.status_code == 404 or "We couldn't find any match" in res.text or "b-error-text" in res.text:
        return False
    return True

def emergency_nordnet_scrape(asset_name: str) -> Tuple[Optional[float], str]:
    """
    If Google Finance breaks, we need an immediate static price patch to prevent 
    the #N/A! error from cascading through the user's entire Google Sheet.
    """
    url = f"https://www.nordnet.se/api/2/instruments?query={urllib.parse.quote(asset_name)}"
    headers = {'client-id': 'NEXT', 'User-Agent': 'Mozilla/5.0'}
    
    res = robust_get(url, use_cffi=False, headers=headers, max_retries=2)
    if res and res.status_code == 200:
        try:
            data = res.json()
            if len(data) > 0:
                hit = data[0]
                price = hit.get('last_price') or hit.get('nav')
                if price is not None:
                    return float(price), hit.get('currency', 'SEK')
        except Exception:
            pass
    return None, "SEK"


# ==========================================
# 2. THE MASTER VALIDATION ENGINE
# ==========================================

def run_validation_agent(portfolio_df: pd.DataFrame = None, transactions_df: pd.DataFrame = None) -> pd.DataFrame:
    print("\n🛡️ Booting up the Omniscient QA Validation Agent...")

    # 1. Ingestion & State Check
    if portfolio_df is None:
        if not PORTFOLIO_FILE.exists(): return pd.DataFrame()
        portfolio_df = pd.read_csv(PORTFOLIO_FILE, keep_default_na=False)

    if transactions_df is None:
        if not TRANSACTIONS_FILE.exists(): return pd.DataFrame()
        transactions_df = pd.read_csv(TRANSACTIONS_FILE, keep_default_na=False)

    warnings: List[str] = []
    fixes_made = 0

    # ==========================================
    # PHASE A: LEDGER PHYSICS & TRANSACTIONS
    # ==========================================
    print("   -> Running Phase A: Double-Entry Physics Audit...")

    duplicates_portfolio = portfolio_df[portfolio_df.duplicated(subset=['Name'], keep=False)]
    if not duplicates_portfolio.empty:
        warnings.append(f"[CRITICAL] Found {len(duplicates_portfolio)} duplicate asset names in the final ledger!")

    # Check for raw CSV export duplicates (Excluding 0.00 SEK to catch corporate splits)
    tx_check = transactions_df[transactions_df['Asset'] != 'SEK CASH'].copy()
    subset_keys = ['Date', 'Asset', 'Original_Type', 'Quantity', 'Amount_SEK', 'Bank', 'Account']
    duplicates_tx = tx_check[tx_check.duplicated(subset=subset_keys, keep=False)]

    if not duplicates_tx.empty:
        warnings.append(f"[WARNING] Found {len(duplicates_tx)} potential duplicate entries in raw transactions.")
        sorted_dupes = duplicates_tx[subset_keys].sort_values(['Date', 'Asset'])
        sorted_dupes.to_csv(DUPLICATES_FILE, index=False, encoding='utf-8-sig')

    # Cash Pool Margin Check
    cash_row = portfolio_df[portfolio_df['Name'] == 'SEK CASH']
    if not cash_row.empty:
        cash_balance = float(cash_row['Units'].values[0])
        if cash_balance < -1.0: # Floating point buffer
            warnings.append(f"[WARNING] SEK CASH balance dropped to {cash_balance:.2f}. Did you utilize margin/leverage?")
    else:
        warnings.append("[CRITICAL] 'SEK CASH' anchor row is completely missing!")

    # Negative Matter Check
    for _, row in portfolio_df.iterrows():
        name = row['Name']
        if not name or name == 'SEK CASH': continue
        units = float(row['Units'])
        avg_buy = float(row['Average Buy Price'])
        if units < -0.0001:
            warnings.append(f"[MATH ERROR] {name} has negative units ({units}). Missing a BUY or TRANSFER_IN?")
        if avg_buy < -0.0001:
            warnings.append(f"[MATH ERROR] {name} has a negative average buy price ({avg_buy}).")

    # Transfer Volume Reconciliation
    total_in = transactions_df[transactions_df['Standard_Type'] == 'TRANSFER_IN']['Quantity'].astype(float).sum()
    total_out = transactions_df[transactions_df['Standard_Type'] == 'TRANSFER_OUT']['Quantity'].astype(float).sum()
    if abs(total_in - total_out) > 0.1:
         warnings.append(f"[WARNING] Unbalanced transfers detected. Transfer IN units: {total_in:.2f} | Transfer OUT units: {total_out:.2f}. Check for lost shares in transit.")

    # ==========================================
    # PHASE B: GOOGLE FINANCE TICKER AUDIT
    # ==========================================
    print("   -> Running Phase B: Live Ticker Connection Audit...")

    ticker_map = {}
    if MAPPING_FILE.exists():
        with open(MAPPING_FILE, "r", encoding="utf-8") as f: ticker_map = json.load(f)

    for idx, row in portfolio_df.iterrows():
        gf_ticker = str(row['GF Ticker'])
        asset_name = row['Name']
        units = float(row['Units'])
        live_price_str = str(row['Live Price'])

        if pd.isna(live_price_str) or live_price_str.strip() == "":
             warnings.append(f"[FORMULA ERROR] {asset_name} is missing a live price formula completely.")

        if gf_ticker != "N/A" and units > 0.001:
            is_valid = is_google_finance_ticker_alive(gf_ticker)
            time.sleep(0.15) 

            if not is_valid:
                print(f"      [AGENT ALERT] Google Finance 404'd '{gf_ticker}' for {asset_name}. Patching...")
                fallback_price, fallback_currency = emergency_nordnet_scrape(asset_name)

                if fallback_price:
                    price_str = str(round(float(fallback_price), 4))
                    if fallback_currency.upper() not in ["SEK", "N/A"]:
                        portfolio_df.at[idx, 'Live Price'] = f'={price_str} * GOOGLEFINANCE("CURRENCY:{fallback_currency}SEK")'
                    else:
                        portfolio_df.at[idx, 'Live Price'] = f'={price_str}'
                    portfolio_df.at[idx, 'GF Ticker'] = "N/A"
                    fixes_made += 1
                    if asset_name in ticker_map:
                        ticker_map[asset_name]["ticker"] = "N/A"
                        ticker_map[asset_name]["fallback_price"] = fallback_price
                        ticker_map[asset_name]["fallback_currency"] = fallback_currency
                else:
                    warnings.append(f"[DATA LOSS] {asset_name} is delisted and no fallback price could be scraped. Zeroing value.")
                    portfolio_df.at[idx, 'Live Price'] = "0"
                    portfolio_df.at[idx, 'GF Ticker'] = "N/A"
                    fixes_made += 1
                time.sleep(0.5)

    # Save the verified portfolio for downstream execution
    portfolio_df.to_csv(VERIFIED_FILE, index=False, encoding='utf-8-sig')
    if fixes_made > 0 and ticker_map:
        with open(MAPPING_FILE, "w", encoding="utf-8") as f: json.dump(ticker_map, f, indent=4)

    # ==========================================
    # PHASE C: METRICS COMPUTATION AUDIT
    # ==========================================
    if METRICS_OUTPUT_FILE.exists():
        print("   -> Running Phase C: Portfolio Metrics Math Audit...")
        metrics_df = pd.read_csv(METRICS_OUTPUT_FILE)
        
        # 1. Test Portfolio Weight Sum
        total_weight = pd.to_numeric(metrics_df['Portfolio Weight (%)'], errors='coerce').sum()
        if not (99.0 <= total_weight <= 101.0) and total_weight != 0.0:
            warnings.append(f"[MATH ERROR] Total Portfolio Weight sum equals {total_weight}%. It must equal 100%.")

        # 2. Re-verify the Core Equation
        for _, row in metrics_df.iterrows():
            name = row['Name']
            if name == 'SEK CASH': continue
            
            calc_val = float(row['Units']) * float(row['Real_Live_Price_SEK'])
            rep_val = float(row['Current Value (SEK)'])
            if abs(calc_val - rep_val) > 1.0:
                 warnings.append(f"[MATH ERROR] Value mismatch on {name}. Calc: {calc_val:.2f} vs Rep: {rep_val:.2f}")

    # ==========================================
    # PHASE D: HISTORICAL TIME-MACHINE AUDIT
    # ==========================================
    if HISTORICAL_PERFORMANCE_FILE.exists():
        print("   -> Running Phase D: Historical Timeline Audit...")
        hist_df = pd.read_csv(HISTORICAL_PERFORMANCE_FILE)
        
        # 1. Timeline Continuity Check
        hist_df['Date'] = pd.to_datetime(hist_df['Date'])
        date_diffs = hist_df['Date'].diff().dt.days
        if (date_diffs > 1).any():
             warnings.append("[CRITICAL] Historical timeline is broken. Found gaps larger than 1 calendar day.")

        # 2. Negative Wealth Check
        if (hist_df['Total Portfolio Value (SEK)'] < -1.0).any():
             warnings.append("[MATH ERROR] Historical Portfolio Value dropped below 0 SEK.")

        # 3. Present-Day Synchronization Check
        if METRICS_OUTPUT_FILE.exists():
            final_hist_val = float(hist_df['Total Portfolio Value (SEK)'].iloc[-1])
            live_sys_val = pd.to_numeric(metrics_df['Current Value (SEK)'], errors='coerce').sum()
            # If the discrepancy is > 200 SEK (allowing for minor live FX micro-fluctuations), raise an alarm
            if abs(final_hist_val - live_sys_val) > 200.0:
                 warnings.append(f"[SYNC ERROR] Time Machine desynced from Live Ledger! Hist: {final_hist_val:.0f} vs Live: {live_sys_val:.0f}")

    # ==========================================
    # REPORT SUMMARY
    # ==========================================
    print("\n--- MASTER VALIDATION REPORT ---")
    if not warnings:
        print("✅ FULL SYSTEM VERIFIED. No mathematical, network, or chronological errors detected.")
    else:
        print(f"⚠️ Agent detected {len(warnings)} potential structural integrity warnings:")
        for w in warnings: print(f"    {w}")

    return portfolio_df

if __name__ == "__main__":
    run_validation_agent()