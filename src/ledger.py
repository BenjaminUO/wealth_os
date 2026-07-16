"""
WEALTH OS - DOUBLE-ENTRY PHYSICS ENGINE
Reconstructs portfolio history chronologically from Day 1.
Enforces strict double-entry accounting to determine true Cost Basis,
Historical Invested Capital, and exact Realized Gains.
"""
import pandas as pd
import json
import os
from typing import Dict, Any

# Import Master Configurations and Utilities
from src.config import TRANSACTIONS_FILE, MAPPING_FILE, PORTFOLIO_FILE
from src.utils import get_historical_fx_rate

def generate_portfolio(df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Executes the chronological double-entry ledger.
    Can accept a DataFrame directly from memory (cleaner.py) or load from disk.
    """
    if df is None:
        if not TRANSACTIONS_FILE.exists():
            print(f"🚨 Missing {TRANSACTIONS_FILE.name}. Run cleaner.py first.")
            return pd.DataFrame()
        df = pd.read_csv(TRANSACTIONS_FILE)

    if not MAPPING_FILE.exists():
        print(f"🚨 Missing {MAPPING_FILE.name}. Run scraper.py first.")
        return pd.DataFrame()

    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        known_tickers = json.load(f)

    # 1. Format strict timeline data types
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Asset'] = df['Asset'].fillna("").astype(str)

    # 2. INTRA-DAY CAUSALITY MATRIX
    # Guarantees that if multiple events happen on the exact same day, 
    # they execute in the strict logical direction of time.
    orders = {
        'BUY': 1, 'SPINOFF': 2, 'SPLIT': 3, 'TRANSFER_IN': 4, 
        'SELL': 5, 'TRANSFER_OUT': 6, 'DIVIDEND': 7, 'TAX': 8, 'FEE': 9, 'OTHER': 10
    }
    df['Order'] = df['Standard_Type'].apply(lambda c: orders.get(c, 10))
    df = df.sort_values(['Date', 'Order']).reset_index(drop=True)

    # 3. Initialize the Master Ledger
    portfolio: Dict[str, Dict[str, Any]] = {}

    def init_asset(asset_name: str):
        if asset_name not in portfolio:
            portfolio[asset_name] = {
                'Units': 0.0, 'Cost': 0.0, 'Last_GAV': 0.0,
                'Total_Sold_Value': 0.0, 'Units_Sold': 0.0, 'Realized_Gain': 0.0,
                'Dividends': 0.0, 'Taxes_Paid': 0.0, 'Is_Trackable': True,
                'Historical_Cost_Sold': 0.0
            }

    # Ensure SEK CASH (The Universal Anchor) always exists
    init_asset('SEK CASH')
    portfolio['SEK CASH']['Last_GAV'] = 1.0

    print("\n⏳ Reconstructing portfolio physics chronologically from Day 1...")

    # ==========================================
    # 4. THE TIME MACHINE LOOP
    # ==========================================
    for _, r in df.iterrows():
        asset = r['Asset']
        cat = r['Standard_Type']
        tx_date = r['Date']
        
        if asset == "": continue

        # Safely parse absolute numerical values to prevent broker negative-sign glitches
        qty = abs(float(r['Quantity'])) if pd.notna(r.get('Quantity')) else 0.0
        amt = abs(float(r['Amount_SEK'])) if pd.notna(r.get('Amount_SEK')) else 0.0
        raw_qty = float(r['Quantity']) if pd.notna(r.get('Quantity')) else 0.0

        init_asset(asset)
        p = portfolio[asset]
        cash_p = portfolio['SEK CASH']
        
        # Calculate Current GAV before mutation
        gav = p['Cost'] / p['Units'] if p['Units'] > 0 else p['Last_GAV']

        # --- CASH POOL ONLY ---
        if cat == 'DEPOSIT':
            cash_p['Units'] += amt; cash_p['Cost'] += amt

        elif cat == 'WITHDRAWAL':
            cash_p['Units'] -= amt; cash_p['Cost'] -= amt

        elif cat == 'INTEREST':
            cash_p['Units'] += amt; cash_p['Dividends'] += amt

        # --- ASSET & CASH INTERACTIONS ---
        elif cat == 'BUY':
            if qty > 0:
                p['Units'] += qty
                p['Cost'] += amt
                p['Last_GAV'] = p['Cost'] / p['Units']
            # Cash is ALWAYS deducted, even for 0-quantity fractional fee corrections
            cash_p['Units'] -= amt; cash_p['Cost'] -= amt

        elif cat == 'SELL':
            if qty > 0:
                # Quarantine asset if we sell shares we mathematically don't own (broker missing data)
                if p['Units'] < qty and p['Cost'] == 0: 
                    p['Is_Trackable'] = False
                    
                p['Units'] -= qty
                p['Total_Sold_Value'] += amt
                p['Units_Sold'] += qty
                p['Realized_Gain'] += (amt - (qty * gav))

                # Fractional Dust Sweeper
                if p['Units'] <= 0.000001:
                    p['Historical_Cost_Sold'] += p['Cost']
                    p['Units'], p['Cost'] = 0.0, 0.0
                else:
                    # Permanently lock in the exact historical SEK value of this specific sale
                    p['Historical_Cost_Sold'] += (qty * gav)
                    p['Cost'] -= (qty * gav)

                cash_p['Cost'] += (qty * gav)
            else:
                p['Realized_Gain'] += amt

            cash_p['Units'] += amt

        elif cat == 'DIVIDEND':
            p['Dividends'] += amt
            cash_p['Units'] += amt

        elif cat == 'TAX':
            p['Taxes_Paid'] += amt
            cash_p['Units'] -= amt

        elif cat == 'TAX_REFUND':
            p['Taxes_Paid'] -= amt
            cash_p['Units'] += amt

        elif cat == 'FEE':
            p['Realized_Gain'] -= amt
            cash_p['Units'] -= amt

        # --- CORPORATE ACTIONS & TRANSFERS ---
        elif cat == 'SPINOFF':
            # Spinoff adds units but strictly locks cost, forcing exact GAV dilution
            p['Units'] += raw_qty
            if p['Units'] > 0: 
                p['Last_GAV'] = p['Cost'] / p['Units']
            else: 
                p['Units'], p['Cost'] = 0.0, 0.0
                
        elif cat == 'SPLIT':
            # Splits adjust units exactly as the broker reported, locking Cost natively
            p['Units'] += raw_qty
            if p['Units'] > 0: 
                p['Last_GAV'] = p['Cost'] / p['Units']
            else: 
                p['Units'], p['Cost'] = 0.0, 0.0
                
        elif cat == 'TRANSFER_OUT':
            if qty > 0:
                if p['Units'] < qty and p['Cost'] == 0:
                     p['Is_Trackable'] = False
                p['Units'] -= qty
                
                # --- REMOVE THIS BLOCK ---
                # if p['Units'] <= 0.000001:
                #      p['Units'], p['Cost'] = 0.0, 0.0
                # else:
                #      p['Cost'] -= qty * gav
                # -------------------------
                
                # Replace with:
                p['Cost'] -= (qty * gav)
                # CRITICAL: We DO NOT add to Historical_Cost_Sold here. Internal transfers are not sales!
                
        elif cat == 'TRANSFER_IN':
            if qty > 0:
                # THE TRANSIT VAULT FIX: Use the historical memory (Last_GAV) if units dropped to 0 during transit
                neutral_gav = gav if gav > 0 else p['Last_GAV']
                p['Units'] += qty
                price_val = abs(float(r['Price'])) if pd.notna(r.get('Price')) else 0.0
                transaction_label = f"{str(r.get('Original_Type', '')).upper()} {str(r.get('Type', '')).upper()}"
                is_subscription_event = any(token in transaction_label for token in ['TECKNING', 'TILLDELNING', 'NYEMISSION'])

                if amt > 0:
                    # Explicit cash amount was attached by the broker
                    p['Cost'] += amt
                elif is_subscription_event and price_val > 0:
                    # Rights/subscription events should use the explicit subscription price, not the previous average.
                    p['Cost'] += (qty * price_val)
                elif neutral_gav > 0:
                    # THE BROKER TRANSFER RE-INJECTION: Cost is re-injected perfectly to neutralize TRANSFER_OUT
                    p['Cost'] += (qty * neutral_gav)
                elif price_val > 0:
                    # EXTERNAL TRANSFER: Asset originating outside the tracked ecosystem
                    mapping_data = known_tickers.get(asset, {})
                    asset_currency = mapping_data.get("fallback_currency", "SEK")
                    
                    if asset_currency.upper() not in ["SEK", "N/A", ""]:
                        # THE BULLETPROOF FX SHIELD (Tuple unpacks seamlessly)
                        fx_rate, pence_multiplier = get_historical_fx_rate(asset_currency, tx_date)
                        p['Cost'] += (qty * price_val * pence_multiplier * fx_rate)
                    else:
                        p['Cost'] += (qty * price_val)

                p['Last_GAV'] = p['Cost'] / p['Units'] if p['Units'] > 0 else p['Last_GAV']

    # ==========================================
    # 5. GOOGLE SHEETS COMPILATION
    # ==========================================
    filtered_assets = []
    
    for asset, data in portfolio.items():
        if asset != 'SEK CASH':
            # Skip completely dead assets with zero financial footprint
            if data['Units'] < 0.001 and data['Units_Sold'] < 0.001 and abs(data['Realized_Gain']) < 0.01 and abs(data['Dividends']) < 0.01: 
                continue
                
            # Memory Quarantine: Protects Google Sheet math from untrackable assets
            if not data['Is_Trackable']: 
                data['Units'] = 0.0
                data['Cost'] = 0.0

        mapping_data = known_tickers.get(asset, {})
        gf_ticker = mapping_data.get("ticker", "N/A")
        fallback_price = mapping_data.get("fallback_price", None)
        fallback_currency = mapping_data.get("fallback_currency", "SEK")
        
        filtered_assets.append((asset, data, gf_ticker, fallback_price, fallback_currency))

    # Sort: Tickers first, then by current value
    filtered_assets.sort(key=lambda x: (x[2] if x[2] != "N/A" else "ZZZ", x[1]['Units']), reverse=True)
    
    results = []
    row_num = 2

    for asset, data, gf_ticker, fallback_price, fallback_currency in filtered_assets:
        u = data['Units']
        final_gav = data['Cost'] / u if u > 0 else data['Last_GAV']
        avg_sell = data['Total_Sold_Value'] / data['Units_Sold'] if data['Units_Sold'] > 0 else 0.0
        
        # True Historical Invested Capital (Protects ROI denominator from shrinking)
        total_invested = data['Cost'] + data['Historical_Cost_Sold']
        net_dividends = data['Dividends'] - data['Taxes_Paid']

        # --- GOOGLE SHEETS FORMULA INJECTION ---
        if asset == 'SEK CASH':
            live_price_formula = "1"
            unrealized_formula = "0"
            final_gav = 1.0
            
        elif gf_ticker != "N/A" and u > 0.001:
            # Dynamic currency conversion logic protecting LSE ETFs (Row-Agnostic)
            live_price_formula = (
                f'=GOOGLEFINANCE(INDIRECT("A"&ROW()), "price") * '
                f'IF(AND(ISNUMBER(SEARCH("LON:", INDIRECT("A"&ROW()))), IFERROR(GOOGLEFINANCE(INDIRECT("A"&ROW()), "currency"), "")="GBP"), 0.01, 1) * '
                f'IFERROR(GOOGLEFINANCE("CURRENCY:" & GOOGLEFINANCE(INDIRECT("A"&ROW()), "currency") & "SEK"), 1)'
            )
            unrealized_formula = f'=(INDIRECT("F"&ROW()) * INDIRECT("C"&ROW())) - (INDIRECT("C"&ROW()) * INDIRECT("D"&ROW()))'
            
        elif fallback_price is not None and str(fallback_price) != "DELISTED" and u > 0.001:
            price_str = str(round(float(fallback_price), 4))
            
            if fallback_currency.upper() not in ["SEK", "N/A"]:
                safe_currency = "GBP" if fallback_currency.upper() == "GBP" else fallback_currency.upper()
                if fallback_currency == "GBp":
                     live_price_formula = f'=({price_str} * 0.01) * GOOGLEFINANCE("CURRENCY:GBPSEK")'
                else:
                     live_price_formula = f'={price_str} * GOOGLEFINANCE("CURRENCY:{safe_currency}SEK")'
            else:
                 live_price_formula = price_str
                 
            unrealized_formula = f'=(INDIRECT("F"&ROW()) * INDIRECT("C"&ROW())) - (INDIRECT("C"&ROW()) * INDIRECT("D"&ROW()))'
            
        else:
            live_price_formula = "0"
            unrealized_formula = f'=(INDIRECT("F"&ROW()) * INDIRECT("C"&ROW())) - (INDIRECT("C"&ROW()) * INDIRECT("D"&ROW()))' if u > 0.001 else "0"

        total_gain_formula = f'=INDIRECT("H"&ROW()) + INDIRECT("I"&ROW()) + INDIRECT("J"&ROW())'
        current_value_formula = f'=INDIRECT("C"&ROW()) * INDIRECT("F"&ROW())'
        
        # Fixing the "Pure Profit" sort bug & dynamic denominator
        if total_invested > 0.01:
            roi_formula = f'=INDIRECT("K"&ROW()) / INDIRECT("L"&ROW())'
        else:
            roi_formula = '""'

        results.append({
            'GF Ticker': gf_ticker, 
            'Name': asset, 
            'Units': round(u, 6), 
            'Average Buy Price': round(final_gav, 2),
            'Average Sell Price': round(avg_sell, 2), 
            'Live Price': live_price_formula, 
            'Current Value (SEK)': current_value_formula,
            'Realized Gains': round(data['Realized_Gain'], 2),
            'Net Dividends': round(net_dividends, 2), 
            'Unrealized Gains': f'{unrealized_formula}',
            'Total Net Gain/Loss (SEK)': total_gain_formula, 
            
            # --- NEW: DEDICATED HISTORICAL MEMORY COLUMN ---
            'Total Invested Capital (SEK)': round(total_invested, 2),
            
            'Historical ROI (%)': roi_formula
        })
        row_num += 1

    final_df = pd.DataFrame(results)
    final_df.to_csv(PORTFOLIO_FILE, index=False, encoding='utf-8-sig')
    print(f"✅ Success! Double-Entry Engine compiled and saved to '{PORTFOLIO_FILE.name}'")
    return final_df

if __name__ == "__main__":
    generate_portfolio()