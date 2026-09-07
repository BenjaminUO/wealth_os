"""
WEALTH OS - LIVE VALUATION & VISUALIZATION ENGINE
Calculates exact real-time market value, true ROI, and portfolio weights using
asynchronous batch price fetching. Generates institutional-grade Plotly dashboards.
"""

import pandas as pd
import numpy as np
import json
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import sys
import time
from pathlib import Path
from typing import Dict, Any

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Import Master Configurations and Utilities
from src.config import VERIFIED_FILE, MAPPING_FILE, METRICS_OUTPUT_FILE, PROCESSED_DIR, MANUAL_CURRENCY_OVERRIDES
from src.utils import google_to_yahoo, get_yf_currency, get_live_fx_rate


# ==========================================
# 1. BATCH NETWORK ENGINE
# ==========================================

def batch_fetch_live_prices(gf_tickers: pd.Series) -> Dict[str, float]:
    """
    Prevents API Bans (HTTP 429) by downloading all live prices in a chunked, 
    highly optimized batch request rather than looping sequentially.
    """
    print("\n🔄 Compiling global tickers for chunked market data download...")
    
    # Translate Google prefixes to Yahoo suffixes
    yf_symbols = [google_to_yahoo(t) for t in gf_tickers.dropna().unique() if t != "N/A"]
    valid_symbols = list(set([sym for sym in yf_symbols if sym]))

    live_prices = {}
    if not valid_symbols: 
        return live_prices

    # --- THE CHUNKED DOWNLOAD SHIELD (Prevents Yahoo from dropping columns) ---
    chunk_size = 50
    chunks = [valid_symbols[i:i + chunk_size] for i in range(0, len(valid_symbols), chunk_size)]
    
    for chunk in chunks:
        try:
            # THE WEEKEND FIX: High-speed batch download spanning 5 days to cover weekends/holidays
            batch_data = yf.download(chunk, period="5d", progress=False)
            
            if not batch_data.empty:
                # THE MULTI-INDEX SHIELD: Safely navigates the MultiIndex or single Series return
                if isinstance(batch_data.columns, pd.MultiIndex):
                    if 'Close' in batch_data.columns.levels[0]:
                        close_data = batch_data['Close']
                        for ticker in chunk:
                            if ticker in close_data.columns:
                                clean_s = close_data[ticker].ffill().dropna()
                                if not clean_s.empty: 
                                    live_prices[ticker] = float(clean_s.iloc[-1])
                else:
                    if 'Close' in batch_data.columns:
                        close_data = batch_data['Close']
                        if isinstance(close_data, pd.Series):
                            clean_s = close_data.ffill().dropna()
                            if not clean_s.empty: 
                                live_prices[chunk[0]] = float(clean_s.iloc[-1])
                        else:
                            for ticker in chunk:
                                if ticker in close_data.columns:
                                    clean_s = close_data[ticker].ffill().dropna()
                                    if not clean_s.empty: 
                                        live_prices[ticker] = float(clean_s.iloc[-1])
        except Exception as e:
            pass
            
        time.sleep(0.5) # Polite buffer to respect rate limits

    # --- THE INDIVIDUAL RECOVERY SHIELD ---
    # Catches stocks (like HOOD, WBA, FL) that Yahoo randomly drops even in chunked mode
    missing = [t for t in valid_symbols if t not in live_prices]
    if missing:
        print(f"      ⚠️ Yahoo dropped {len(missing)} tickers in bulk. Fetching individually...")
        for t in missing:
            try:
                d = yf.download(t, period="5d", progress=False)
                if not d.empty and 'Close' in d.columns:
                    clean_s = d['Close'].ffill().dropna()
                    if not clean_s.empty: 
                        live_prices[t] = float(clean_s.iloc[-1])
            except Exception: 
                pass

    return live_prices


# ==========================================
# 2. CORE MATHEMATICS ENGINE
# ==========================================

def calculate_master_metrics(df: pd.DataFrame, ticker_map: Dict[str, Any]) -> pd.DataFrame:
    """Natively computes live market values in exact SEK."""
    
    # 1. Enforce strict numerical data types from the Google Sheets CSV format
    numeric_cols = ['Units', 'Average Buy Price', 'Realized Gains', 'Net Dividends', 'Total Invested Capital (SEK)']
    for col in numeric_cols:
         df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
         
    df['Cost Basis (SEK)'] = df['Units'] * df['Average Buy Price']
    df['Real_Live_Price_SEK'] = 0.0
    
    # 2. Execute Batch Download
    batch_prices = batch_fetch_live_prices(df['GF Ticker'])
    print("🧮 Calculating exact real-time valuations and FX conversions...")

    for idx, row in df.iterrows():
        asset = row['Name']
        gf_ticker = row['GF Ticker']
        units = row['Units']

        if asset == 'SEK CASH':
            df.at[idx, 'Real_Live_Price_SEK'] = 1.0
            continue
            
        if units <= 0.0001: 
            continue

        price_sek = 0.0

        # --- STRATEGY A: Listed Assets (via Batch Data) ---
        if gf_ticker != "N/A":
            yf_symbol = google_to_yahoo(gf_ticker)
            if yf_symbol in batch_prices:
                raw_price = batch_prices[yf_symbol]
                
                # THE TRUE CURRENCY FIX
                curr, price_multiplier = get_yf_currency(yf_symbol)
                
                # --- NEW: THE MANUAL CURRENCY INTERCEPTOR ---
                # This explicitly overrides the utils.py '.ST = SEK' fast-path
                if asset in MANUAL_CURRENCY_OVERRIDES:
                    curr = MANUAL_CURRENCY_OVERRIDES[asset]
                
                # Fetch exact FX rate and apply Pence anomaly protections
                fx_rate, fx_pence_mult = get_live_fx_rate(curr)
                
                # Calculate True SEK Price 
                price_sek = raw_price * price_multiplier * fx_pence_mult * fx_rate

        # --- STRATEGY B: Unlisted Mutual Funds (via Scraped NAVs) ---
        if price_sek == 0.0 and asset in ticker_map:
            asset_data = ticker_map[asset]
            fallback_p = asset_data.get("fallback_price")
            fallback_c = asset_data.get("fallback_currency", "SEK")
            
            if fallback_p and str(fallback_p) != "DELISTED":
                # Let utils.py handle the Pence anomaly natively!
                fx_rate, pence_multiplier = get_live_fx_rate(fallback_c)
                price_sek = float(fallback_p) * pence_multiplier * fx_rate

        # --- THE ABSOLUTE FALLBACK SHIELD ---
        # If live price AND scraped NAV fail, value asset at Cost Basis 
        # so your capital doesn't disappear from the total portfolio value
        if price_sek <= 0.0 and float(row['Average Buy Price']) > 0:
            price_sek = float(row['Average Buy Price'])
            if units > 0:
                print(f"      ⚠️ Valuing {asset} at Cost Basis ({price_sek:.2f}) - Live Fetch Failed")

        df.at[idx, 'Real_Live_Price_SEK'] = price_sek

    # 3. Recompute strict financial equations using validated real numbers
    df['Current Value (SEK)'] = df['Units'] * df['Real_Live_Price_SEK']
    df['Unrealized Gain (SEK)'] = np.where(
        df['Name'] == 'SEK CASH', 
        0.0, 
        df['Current Value (SEK)'] - df['Cost Basis (SEK)']
    )
    df['Total Profit (SEK)'] = df['Realized Gains'] + df['Net Dividends'] + df['Unrealized Gain (SEK)']

    # --- DELETE THESE TWO LINES ---
    # df['Total Invested Capital (SEK)'] = df['Historical ROI (%)'].astype(str).str.extract(r'/ ([\d\.]+)').astype(float)
    # df['Total Invested Capital (SEK)'] = df['Total Invested Capital (SEK)'].fillna(df['Cost Basis (SEK)'])
    # ------------------------------

    # Calculate True Performance Metrics
    safe_invested = df['Total Invested Capital (SEK)'].replace(0, np.nan)
    df['Profitability (%)'] = (df['Total Profit (SEK)'] / safe_invested * 100).fillna(0.0).round(2)
    df['Yield on Cost (%)'] = (df['Net Dividends'] / safe_invested * 100).fillna(0.0).round(2)

    # --- THE MARKET WIPEOUT SHIELD ---
    # Prevents ZeroDivisionError if the entire portfolio's net worth drops to 0.0 SEK
    total_market_value = df['Current Value (SEK)'].sum()
    if total_market_value > 0.01:
        df['Portfolio Weight (%)'] = (df['Current Value (SEK)'] / total_market_value * 100).round(2)
    else:
        df['Portfolio Weight (%)'] = 0.0

    # Build comprehensive hover-text for the Plotly Dashboards
    df['Hover Text'] = (
        df['Name'] + 
        "<br>Live Value: " + df['Current Value (SEK)'].fillna(0).astype(int).astype(str) + " SEK" +
        "<br>Weight: " + df['Portfolio Weight (%)'].astype(str) + "%" +
        "<br>Profit: " + df['Profitability (%)'].astype(str) + "%"
    )
    
    return df


# ==========================================
# 3. INSTITUTIONAL VISUALIZATION ENGINE
# ==========================================

def generate_master_visualizations(active_equities: pd.DataFrame, full_df: pd.DataFrame):
    """Generates 4 institutional-grade HTML interactive charts."""
    print("📊 Generating institutional-grade HTML dashboards...")
    
    dark_layout = dict(
        template='plotly_dark', 
        paper_bgcolor='#1E1E1E', 
        plot_bgcolor='#1E1E1E', 
        font=dict(color='#E0E0E0')
    )

    # 1. Allocation Donut (Top 15 by Live Value plus liquidity)
    top_15 = active_equities.nlargest(15, 'Current Value (SEK)').copy()
    cash_row = full_df[full_df['Name'] == 'SEK CASH']
    cash_value = float(cash_row['Current Value (SEK)'].sum()) if not cash_row.empty else 0.0
    cash_data = pd.DataFrame([{
        'Name': 'Liquidity (SEK CASH)',
        'Current Value (SEK)': cash_value
    }])
    pie_data = pd.concat([top_15, cash_data], ignore_index=True)

    other_value = active_equities[
        ~active_equities['Name'].isin(top_15['Name'])
    ]['Current Value (SEK)'].sum()
    
    if other_value > 0:
        other_row = pd.DataFrame([{'Name': 'Other Assets', 'Current Value (SEK)': other_value}])
        pie_data = pd.concat([pie_data, other_row], ignore_index=True)

    csn_row = full_df[full_df['Name'] == 'CSN Lån']
    csn_value = abs(float(csn_row['Units'].sum())) if not csn_row.empty else 0.0
    gross_value = pie_data['Current Value (SEK)'].sum()
    csn_ratio_pct = csn_value / gross_value * 100 if gross_value > 0 else 0.0
    liquidity_pull = [
        0.08 if name == 'Liquidity (SEK CASH)' else 0.0
        for name in pie_data['Name']
    ]

    fig1 = px.pie(
        pie_data, values='Current Value (SEK)', names='Name', 
        title=f'Portfolio Allocation (Top 15 by Live Value) | CSN Lån: {csn_ratio_pct:.1f}% of Gross Value',
        hole=0.4
    )
    fig1.update_traces(
        textposition='inside',
        textinfo='percent+label',
        pull=liquidity_pull,
        marker=dict(line=dict(color='#E0E0E0', width=1))
    )
    fig1.update_layout(**dark_layout)

    # 2. Cash Generators Stacked Bar
    top_profits = full_df.nlargest(10, 'Total Profit (SEK)')
    fig2 = go.Figure(data=[
        go.Bar(name='Realized + Unrealized Gains', x=top_profits['Name'], 
               y=top_profits['Realized Gains'] + top_profits['Unrealized Gain (SEK)'], 
               marker_color='#2ECC71'),
        go.Bar(name='Net Dividends', x=top_profits['Name'], 
               y=top_profits['Net Dividends'], 
               marker_color='#F1C40F')
    ])
    fig2.update_layout(barmode='stack', title='Top 10 Lifetime Wealth Generators', **dark_layout)

    # 3. The Risk/Reward Bubble Chart
    fig3 = px.scatter(
        active_equities, x='Current Value (SEK)', y='Profitability (%)', 
        size='Units', color='Name', log_x=True, hover_data=['Hover Text'], 
        title="Position Size (Log-X) vs. ROI (%) - Bubble Size = Total Units"
    )
    fig3.update_layout(**dark_layout)

    # 4. Master Portfolio Treemap (Heatmap)
    treemap_data = active_equities[active_equities['Current Value (SEK)'] > 0].copy()
    treemap_data['Root'] = 'Master Portfolio'
    
    fig4 = px.treemap(
        treemap_data, path=['Root', 'Name'], values='Current Value (SEK)', 
        color='Profitability (%)', color_continuous_scale='RdYlGn', 
        color_continuous_midpoint=0, hover_data=['Hover Text'], 
        title="Master Portfolio Heatmap (Size = Live Value, Color = Profitability %)"
    )
    fig4.update_traces(textinfo="label+value")
    fig4.update_layout(**dark_layout)

    # Output to File
    fig1.write_html(PROCESSED_DIR / "Viz_1_Allocation_Donut.html")
    fig2.write_html(PROCESSED_DIR / "Viz_2_Cash_Generators_Bar.html")
    fig3.write_html(PROCESSED_DIR / "Viz_3_Risk_Reward_Bubble.html")
    fig4.write_html(PROCESSED_DIR / "Viz_4_Master_Heatmap_Treemap.html")
    print("      ✅ Dashboards generated successfully.")


# ==========================================
# 4. EXECUTION
# ==========================================

def run_metrics_and_viz(verified_df: pd.DataFrame = None) -> pd.DataFrame:
    """Orchestrates the valuation and visualization pipeline."""
    
    if verified_df is None:
        if not VERIFIED_FILE.exists() or not MAPPING_FILE.exists():
            print(f"🚨 Missing workspace dependencies. Please run the validation script first.")
            return pd.DataFrame()
        verified_df = pd.read_csv(VERIFIED_FILE, keep_default_na=False)

    with open(MAPPING_FILE, "r", encoding="utf-8") as f: 
        ticker_map = json.load(f)

    # Calculate live metrics
    metrics_df = calculate_master_metrics(verified_df, ticker_map)
    
    # Save metrics cleanly for the downstream AI Agents to read
    metrics_df.to_csv(METRICS_OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"💾 Live Metrics saved securely to {METRICS_OUTPUT_FILE.name}")

    # Filter out dead assets and cash for the visualizations
    active_equities = metrics_df[(metrics_df['Units'] > 0.001) & (metrics_df['Name'] != 'SEK CASH')].copy()
    
    if active_equities.empty:
        print("⚠️ Your portfolio appears to have no active equities. Skipping visualizations.")
        return metrics_df

    # Generate the charts
    generate_master_visualizations(active_equities, metrics_df)
    
    return metrics_df

if __name__ == "__main__":
    run_metrics_and_viz()