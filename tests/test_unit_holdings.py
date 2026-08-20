import pandas as pd
from pathlib import Path

def resolve_path(rel_path: str) -> Path:
    p = Path(rel_path)
    if p.exists(): return p
    p_up = Path("..") / rel_path
    if p_up.exists(): return p_up
    return p

def get_unit_impact(row):
    cat = str(row.get('Standard_Type', ''))
    qty = abs(float(row.get('Quantity', 0.0))) if pd.notna(row.get('Quantity')) else 0.0
    raw_qty = float(row.get('Quantity', 0.0)) if pd.notna(row.get('Quantity')) else 0.0
    orig = str(row.get('Original_Type', '')).upper()
    
    if cat in ['BUY', 'TRANSFER_IN']: 
        return qty
    if cat in ['SELL', 'TRANSFER_OUT']: 
        return -qty
    if cat == 'SPINOFF': 
        return raw_qty
    if cat == 'SPLIT':
        if any(term in orig for term in ['UTTAG', 'SÄLJ', 'INLÖSEN']): return -qty
        elif 'INLÄGG' in orig: return qty
        else: return raw_qty
    return 0.0

def run_units_test():
    tx_file = resolve_path('data/processed/combined_transactions.csv')
    if not tx_file.exists():
        print(f"❌ Error: Could not find '{tx_file}'. Run cleaner.py / main.py first.")
        return

    df = pd.read_csv(tx_file)
    df['Unit_Delta'] = df.apply(get_unit_impact, axis=1)
    
    # Filter out cash
    equities = df[(df['Asset'] != 'SEK CASH') & (df['Asset'].notna()) & (df['Asset'] != '')].copy()
    
    # Group by Bank, Account, and Asset
    summary = equities.groupby(['Bank', 'Account', 'Asset'])['Unit_Delta'].sum().reset_index()
    summary.rename(columns={'Unit_Delta': 'Net_Units'}, inplace=True)
    summary['Net_Units'] = summary['Net_Units'].round(6)
    
    # Filter out closed positions (0 units)
    active_units = summary[abs(summary['Net_Units']) > 0.0001].sort_values(['Bank', 'Account', 'Asset'])

    print("\n" + "="*105)
    print(" 📦 WEALTH OS - NET UNIT HOLDINGS AUDIT (BY BROKER & ACCOUNT)")
    print("="*105)
    print(active_units.to_string(index=False))
    print("-" * 105)

    # Anomaly checks
    negative_balances = active_units[active_units['Net_Units'] < 0]
    if not negative_balances.empty:
        print("🚨 CRITICAL ALERT: NEGATIVE UNIT BALANCES DETECTED:")
        print(negative_balances.to_string(index=False))
        print("👉 Cause: Missing BUY or unrecorded TRANSFER_IN before a SELL.")
    else:
        print(f"✅ All {len(active_units)} active account holdings are mathematically positive.")
    print("="*105 + "\n")

if __name__ == "__main__":
    run_units_test()