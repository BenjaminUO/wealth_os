"""
WEALTH OS - TIME-SERIES BACKTESTER
Reconstructs the historical growth of the consolidated portfolio day-by-day.
Maps True Portfolio Value against Net Invested Capital and a simulated S&P 500 Shadow Benchmark.
"""

import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import json
import time
from typing import List

# Import Master Configurations and Utilities
from src.config import (
    TRANSACTIONS_FILE, MAPPING_FILE, PROCESSED_DIR, 
    CORE_MACRO_SYMBOLS, FALLBACK_FX_RATES
)
from src.utils import google_to_yahoo, get_yf_currency

# ==========================================
# 1. BATCH MARKET DATA ENGINE
# ==========================================

def fetch_historical_prices(tickers: List[str], start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    """
    Downloads 7 years of historical market data using a robust bulk-with-individual-fallback engine.
    Ensures the timeline is continuous across weekends and holidays.
    """
    print("\n📈 Downloading historical market data & global FX rates in chunks...")
    valid_tickers = list(set([t for t in tickers if t] + CORE_MACRO_SYMBOLS))
    
    # THE START-DATE BUFFER FIX: Buffer by 5 days so a Sunday start can inherit Friday's close
    download_start = start_date - pd.Timedelta(days=5)
    
    chunk_size = 50
    chunks = [valid_tickers[i:i + chunk_size] for i in range(0, len(valid_tickers), chunk_size)]
    data_frames = []
    
    for chunk in chunks:
        try:
            raw_data = yf.download(chunk, start=download_start, end=end_date + pd.Timedelta(days=1), progress=False)
            if not raw_data.empty and 'Close' in raw_data:
                # THE CONCAT SHIELD: Force single-ticker responses into a 2D DataFrame layout
                close_df = raw_data['Close']
                if isinstance(close_df, pd.Series):
                    close_df = close_df.to_frame(name=chunk[0])
                data_frames.append(close_df)
        except Exception:
            pass
        time.sleep(0.5) # Polite pacing to prevent 429 API bans
        
    data = pd.concat(data_frames, axis=1) if data_frames else pd.DataFrame()
    
    # Remove duplicate columns just in case CORE_MACRO_SYMBOLS overlapped chunks
    data = data.loc[:, ~data.columns.duplicated()] 
        
    if not data.empty:
        # THE TIMEZONE POISONING SHIELD: Strip timezone artifacts from Yahoo servers
        if data.index.tz is not None: 
            data.index = data.index.tz_localize(None)
        data.index = data.index.normalize()

    # THE WEEKEND VOID FIX: Continuous calendar with forward-fill
    buffered_calendar = pd.date_range(start=download_start, end=end_date, freq='D').normalize()
    data = data[~data.index.duplicated(keep='last')]
    data = data.reindex(buffered_calendar).ffill()
    
    # Trim the dataframe back to the exact requested start_date
    data = data.loc[start_date:end_date]
    return data

# ==========================================
# 2. TIME-SERIES PHYSICS ENGINE
# ==========================================

def run_historical_backtest():
    if not TRANSACTIONS_FILE.exists() or not MAPPING_FILE.exists(): 
        print(f"🚨 Missing {TRANSACTIONS_FILE.name}. Run the core pipeline first.")
        return

    df = pd.read_csv(TRANSACTIONS_FILE)
    df['Date'] = pd.to_datetime(df['Date'], format='mixed', errors='coerce').dt.normalize()
    df['Asset'] = df['Asset'].fillna("").astype(str)
    df = df.dropna(subset=['Date'])
    
    # --- THE INTRA-DAY CAUSALITY FIX ---
    # Guarantees mathematical safety (e.g. TRANSFER_IN executes before TRANSFER_OUT on the same day)
    orders = {'BUY': 1, 'SPINOFF': 2, 'SPLIT': 3, 'TRANSFER_IN': 4, 'SELL': 5, 'TRANSFER_OUT': 6, 'DIVIDEND': 7, 'TAX': 8, 'FEE': 9, 'OTHER': 10}
    df['Order'] = df['Standard_Type'].apply(lambda c: orders.get(c, 10))
    df = df.sort_values(['Date', 'Order']).reset_index(drop=True)
    
    with open(MAPPING_FILE, "r", encoding="utf-8") as f: 
        mapping = json.load(f)

    start_date = df['Date'].min()
    end_date = pd.Timestamp.today().normalize()
    timeline = pd.date_range(start=start_date, end=end_date, freq='D').normalize()
    
    asset_to_yf = {}
    for asset, data in mapping.items():
        yf_tick = google_to_yahoo(data.get('ticker', 'N/A'))
        if yf_tick and yf_tick != "N/A": 
            asset_to_yf[asset] = yf_tick

    hist_prices = fetch_historical_prices(list(asset_to_yf.values()), start_date, end_date)
    if hist_prices.empty: 
        print("🚨 Failed to download historical data. Aborting backtest.")
        return
    # ==========================================
    # THE MUTUAL FUND INJECTION
    # ==========================================
    fund_history_file = PROCESSED_DIR / "mutual_fund_hist_prices.csv"
    if fund_history_file.exists():
        print("💉 Injecting historical mutual fund NAVs into market data...")
        
        # 1. Load the fund data and ensure the index matches our strict datetime format
        fund_df = pd.read_csv(fund_history_file, index_col='Date', parse_dates=True)
        fund_df.index = fund_df.index.normalize()
        
        # 2. The Weekend Void Fix (Mutual Fund Edition)
        # Reindex to our continuous timeline and forward-fill weekend/holiday gaps
        fund_df = fund_df.reindex(timeline).ffill()
        
        # 3. Merge seamlessly with Yahoo Finance data
        hist_prices = pd.concat([hist_prices, fund_df], axis=1)
        
        # 4. The Pseudo-Ticker Trick
        # Update the lookup dictionary so the daily loop knows the "ticker" is just the fund name
        for fund_name in fund_df.columns:
            asset_to_yf[fund_name] = fund_name
    else:
        print("⚠️ No mutual fund history file found. Unlisted funds will flatline at cost basis.")

    print("🌍 Resolving true asset currencies to prevent FX mismatches...")
    asset_currency_map = {}
    for asset, data in mapping.items():
        yf_tick = google_to_yahoo(data.get('ticker', 'N/A'))
        if yf_tick and yf_tick != "N/A": 
            curr, mult = get_yf_currency(yf_tick)
        else:
            curr = data.get("fallback_currency", "SEK")
            mult = 0.01 if curr == "GBp" else 1.0
            curr = "GBP" if curr == "GBp" else curr
        asset_currency_map[asset] = (curr, mult)

    portfolio_history = []
    unique_assets = df['Asset'].unique()
    running_units = {asset: 0.0 for asset in unique_assets}
    running_cost = {asset: 0.0 for asset in unique_assets}
    running_units['SEK CASH'] = 0.0
    
    shadow_sp500_units = 0.0
    pending_shadow_cash_sek = 0.0
    total_net_deposits = 0.0

    print("⏳ Reconstructing historical portfolio physics day-by-day...")
    df_grouped = df.groupby('Date')

    for current_date in timeline:
        sp_price_usd = float(hist_prices.loc[current_date, 'SPY']) if 'SPY' in hist_prices.columns and pd.notna(hist_prices.loc[current_date, 'SPY']) else None
        usd_sek_rate = float(hist_prices.loc[current_date, 'SEK=X']) if 'SEK=X' in hist_prices.columns and pd.notna(hist_prices.loc[current_date, 'SEK=X']) else FALLBACK_FX_RATES["USD"]

        sp_price_sek = (sp_price_usd * usd_sek_rate) if sp_price_usd else None
        is_trading_day = sp_price_sek is not None and sp_price_sek > 0

        if current_date in df_grouped.groups:
            day_tx = df_grouped.get_group(current_date)
            for _, tx in day_tx.iterrows():
                asset = tx['Asset']
                cat = tx['Standard_Type']
                
                # Force strictly positive amounts for safe double-entry addition/subtraction
                qty = abs(float(tx['Quantity'])) if pd.notna(tx['Quantity']) else 0.0
                amt = abs(float(tx['Amount_SEK'])) if pd.notna(tx['Amount_SEK']) else 0.0
                raw_qty = float(tx['Quantity']) if pd.notna(tx['Quantity']) else 0.0
                price_val = abs(float(tx['Price'])) if pd.notna(tx['Price']) else 0.0
                
                gav = running_cost[asset] / running_units[asset] if running_units[asset] > 0 else 0.0

                if cat == 'DEPOSIT':
                    running_units['SEK CASH'] += amt
                    total_net_deposits += amt
                    pending_shadow_cash_sek += amt
                elif cat == 'WITHDRAWAL':
                    running_units['SEK CASH'] -= amt
                    total_net_deposits -= amt
                    pending_shadow_cash_sek -= amt
                elif cat == 'BUY':
                    if qty > 0: 
                        running_units[asset] += qty
                        running_cost[asset] += amt 
                    running_units['SEK CASH'] -= amt
                elif cat == 'SELL':
                    if qty > 0: 
                        running_units[asset] -= qty
                        running_cost[asset] -= (qty * gav)
                        if running_units[asset] <= 0.000001: 
                            running_units[asset] = 0.0; running_cost[asset] = 0.0
                    running_units['SEK CASH'] += amt
                elif cat == 'TRANSFER_IN':
                    if qty > 0: 
                        is_internal = running_units[asset] > 0
                        running_units[asset] += qty
                        if amt > 0: 
                            running_cost[asset] += amt
                        elif is_internal: 
                            running_cost[asset] += (qty * gav)
                        elif price_val > 0:
                            curr, price_multiplier = asset_currency_map.get(asset, ("SEK", 1.0))
                            if curr == "SEK": fx_rate = 1.0
                            else:
                                fx_ticker = "SEK=X" if curr == "USD" else f"{curr}SEK=X"
                                if fx_ticker in hist_prices.columns and pd.notna(hist_prices.loc[current_date, fx_ticker]): 
                                    fx_rate = float(hist_prices.loc[current_date, fx_ticker])
                                else: 
                                    fx_rate = FALLBACK_FX_RATES.get(curr, 1.0)
                            running_cost[asset] += (qty * price_val * price_multiplier * fx_rate)
                elif cat == 'TRANSFER_OUT':
                    if qty > 0: 
                        running_units[asset] -= qty
                        running_cost[asset] -= (qty * gav)
                        if running_units[asset] <= 0.000001: 
                            running_units[asset] = 0.0; running_cost[asset] = 0.0
                elif cat in ['SPLIT', 'SPINOFF']:
                    running_units[asset] += raw_qty
                    if running_units[asset] <= 0.000001: 
                        running_units[asset] = 0.0; running_cost[asset] = 0.0
                elif cat in ['DIVIDEND', 'TAX_REFUND', 'INTEREST']:
                    running_units['SEK CASH'] += amt
                elif cat in ['TAX', 'FEE']:
                    running_units['SEK CASH'] -= amt

        # Execute Pending Shadow Benchmark Cash
        if is_trading_day and pending_shadow_cash_sek != 0:
            shadow_sp500_units += (pending_shadow_cash_sek / sp_price_sek)
            pending_shadow_cash_sek = 0.0

        daily_value = running_units['SEK CASH']
        for asset, units in running_units.items():
            if units <= 0.001 or asset == 'SEK CASH': 
                continue
                
            yf_tick = asset_to_yf.get(asset)
            
            # --- THE MUTUAL FUND BLACK HOLE RECOVERY ---
            # If the asset has no historical ticker (Unlisted Funds), value it at its running Cost Basis.
            if not yf_tick or yf_tick not in hist_prices.columns or pd.isna(hist_prices.loc[current_date, yf_tick]): 
                daily_value += running_cost[asset]
                continue

            price = float(hist_prices.loc[current_date, yf_tick])
            curr, price_multiplier = asset_currency_map.get(asset, ("SEK", 1.0))
            
            if curr == "SEK": 
                fx_rate = 1.0
            else:
                fx_ticker = "SEK=X" if curr == "USD" else f"{curr}SEK=X"
                if fx_ticker in hist_prices.columns and pd.notna(hist_prices.loc[current_date, fx_ticker]): 
                    fx_rate = float(hist_prices.loc[current_date, fx_ticker])
                else: 
                    fx_rate = FALLBACK_FX_RATES.get(curr, 1.0)
                    
            daily_value += (units * price * price_multiplier * fx_rate)

        shadow_value = pending_shadow_cash_sek
        if is_trading_day: 
            shadow_value += (shadow_sp500_units * sp_price_sek)

        portfolio_history.append({
            'Date': current_date, 
            'Total Portfolio Value (SEK)': round(daily_value, 2),
            'Net Invested Capital (SEK)': round(total_net_deposits, 2), 
            'S&P 500 Shadow Portfolio (SEK)': round(shadow_value, 2)
        })

    # ==========================================
    # 3. EXPORT & VISUALIZATION
    # ==========================================
    history_df = pd.DataFrame(portfolio_history)
    history_df.to_csv(PROCESSED_DIR / "Historical_Performance.csv", index=False)
    
    print("📊 Generating Institutional Backtest Curve...")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df['Date'], y=history_df['S&P 500 Shadow Portfolio (SEK)'], 
        mode='lines', name='S&P 500 Benchmark (Shadow)', 
        line=dict(color='#3498DB', width=2, dash='dot')
    ))
    fig.add_trace(go.Scatter(
        x=history_df['Date'], y=history_df['Total Portfolio Value (SEK)'], 
        mode='lines', name='Actual Portfolio Value', 
        line=dict(color='#2ECC71', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=history_df['Date'], y=history_df['Net Invested Capital (SEK)'], 
        mode='lines', name='Total Net Deposits', 
        line=dict(color='#95A5A6', width=2), fill='tozeroy', fillcolor='rgba(149, 165, 166, 0.1)'
    ))
    fig.update_layout(
        title='Wealth OS: True Portfolio Growth vs. S&P 500 Benchmark', 
        xaxis_title='Date', yaxis_title='Total Value (SEK)', 
        template='plotly_dark', paper_bgcolor='#1E1E1E', plot_bgcolor='#1E1E1E', 
        font=dict(color='#E0E0E0'), hovermode="x unified", 
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor='rgba(30,30,30,0.8)')
    )
    
    output_html = PROCESSED_DIR / "Viz_5_Historical_Backtest.html"
    fig.write_html(output_html)
    print(f"      ✅ Historical backtest complete! 7-year curve saved to '{output_html.name}'")

if __name__ == "__main__":
    run_historical_backtest()