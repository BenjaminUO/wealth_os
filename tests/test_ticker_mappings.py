import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
import pandas as pd
import json
from pathlib import Path

def resolve_path(rel_path: str) -> Path:
    p = Path(rel_path)
    if p.exists(): return p
    p_up = Path("..") / rel_path
    if p_up.exists(): return p_up
    return p

def run_ticker_test():
    tx_file = resolve_path('data/processed/combined_transactions.csv')
    map_file = resolve_path('data/processed/ticker_mapping.json')
    
    if not tx_file.exists():
        print(f"⚠️ Could not find '{tx_file}'. Running the cleaner first...")
        from src.cleaner import clean_and_merge_transactions

        clean_and_merge_transactions()

    if not map_file.exists() and tx_file.exists():
        print(f"⚠️ Could not find '{map_file}'. Generating the ticker mapping...")
        from src.scraper import generate_ticker_mapping

        generate_ticker_mapping()

    if not tx_file.exists() or not map_file.exists():
        print("❌ Error: Missing combined_transactions.csv or ticker_mapping.json.")
        return

    df = pd.read_csv(tx_file)
    with open(map_file, 'r', encoding='utf-8') as f:
        ticker_map = json.load(f)

    # Calculate net units per asset globally
    def get_qty(r):
        cat = str(r.get('Standard_Type', ''))
        q = abs(float(r.get('Quantity', 0.0))) if pd.notna(r.get('Quantity')) else 0.0
        if cat in ['BUY', 'TRANSFER_IN']: return q
        if cat in ['SELL', 'TRANSFER_OUT']: return -q
        return float(r.get('Quantity', 0.0)) if pd.notna(r.get('Quantity')) else 0.0

    df['Delta'] = df.apply(get_qty, axis=1)
    holdings = df[df['Asset'] != 'SEK CASH'].groupby('Asset')['Delta'].sum().reset_index()
    active_holdings = holdings[holdings['Delta'] > 0.001].copy()

    results = []
    for _, row in active_holdings.iterrows():
        asset = row['Asset']
        units = round(row['Delta'], 4)
        
        info = ticker_map.get(asset, {})
        ticker = info.get('ticker', 'N/A')
        fallback_p = info.get('fallback_price')
        fallback_c = info.get('fallback_currency', 'SEK')
        
        flag = "✅ OK"
        if ticker == "N/A" and fallback_p is None:
            flag = "🚨 NO PRICE SOURCE"
        elif ticker != "N/A" and ":" not in ticker:
            flag = "⚠️ MISSING PREFIX"
        elif fallback_p is not None:
            flag = f"NAV: {fallback_p} {fallback_c}"

        results.append({
            'Asset Name': str(asset)[:38],
            'Units Held': units,
            'Assigned Ticker': ticker,
            'Status / Flags': flag
        })

    audit_df = pd.DataFrame(results).sort_values(by=['Status / Flags', 'Asset Name'])
    
    print("\n" + "="*105)
    print(" 🎯 WEALTH OS - TICKER MAPPING & PRICING VERIFICATION")
    print("="*105)
    print(audit_df.to_string(index=False))
    print("-" * 105)
    
    warnings = audit_df[audit_df['Status / Flags'].str.contains('🚨|⚠️')]
    if not warnings.empty:
        print(f"⚠️ Found {len(warnings)} potential ticker anomalies:")
        print(warnings[['Asset Name', 'Assigned Ticker', 'Status / Flags']].to_string(index=False))
        print("👉 Action: Update MANUAL_TICKER_OVERRIDES in 'src/config.py'.")
    else:
        print("✅ All active equity and fund positions have verified price feeds.")
    print("="*105 + "\n")

if __name__ == "__main__":
    run_ticker_test()