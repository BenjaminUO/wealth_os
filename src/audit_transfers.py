import pandas as pd
from src.config import TRANSACTIONS_FILE

def hunt_phantom_shares():
    print("🕵️ Booting up the Transit Vault Auditor...\n")
    
    if not TRANSACTIONS_FILE.exists():
        print(f"Error: {TRANSACTIONS_FILE.name} not found.")
        return

    df = pd.read_csv(TRANSACTIONS_FILE)
    
    # We only care about assets, not cash
    df = df[df['Asset'] != 'SEK CASH'].copy()
    df['Quantity'] = df['Quantity'].astype(float).abs()
    
    # Calculate all incoming vs outgoing shares
    df['Direction'] = df['Standard_Type'].map({
        'BUY': 'IN', 'TRANSFER_IN': 'IN', 'SPINOFF': 'IN', 'SPLIT': 'IN',
        'SELL': 'OUT', 'TRANSFER_OUT': 'OUT'
    })
    
    summary = df.groupby(['Asset', 'Direction'])['Quantity'].sum().unstack(fill_value=0)
    
    if 'IN' not in summary.columns: summary['IN'] = 0.0
    if 'OUT' not in summary.columns: summary['OUT'] = 0.0
    
    summary['Net_Difference'] = summary['IN'] - summary['OUT']
    
    # Only flag severe negative balances (meaning the broker withdrew more shares than they deposited)
    anomalies = summary[summary['Net_Difference'] < -0.01].sort_values(by='Net_Difference')
    
    if anomalies.empty:
        print("✅ All internal transfers and corporate actions are perfectly balanced!")
    else:
        print("🚨 MISMATCH DETECTED: The following assets have a NEGATIVE unit balance (Broker Double-Dip):\n")
        print(anomalies[['IN', 'OUT', 'Net_Difference']].to_string())
        print("\nFix Action: Add these asset names to 'IGNORE_ASSET' in config.py if they are dead rights/warrants,")
        print("or add their Original_Type to the Double-Dip Annihilator in cleaner.py.")

if __name__ == "__main__":
    hunt_phantom_shares()