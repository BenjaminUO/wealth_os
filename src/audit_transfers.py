import pandas as pd
from src.config import TRANSACTIONS_FILE

def hunt_phantom_shares():
    print("🕵️ Booting up the Transit Vault Auditor...\n")
    
    if not TRANSACTIONS_FILE.exists():
        print(f"Error: {TRANSACTIONS_FILE.name} not found.")
        return

    df = pd.read_csv(TRANSACTIONS_FILE)
    
    # Filter only for transfers
    transfers = df[df['Standard_Type'].isin(['TRANSFER_IN', 'TRANSFER_OUT'])]
    
    if transfers.empty:
        print("No transfers found in the ledger.")
        return

    # Group by Asset and calculate the net difference
    summary = transfers.groupby(['Asset', 'Standard_Type'])['Quantity'].sum().unstack(fill_value=0)
    
    # Ensure columns exist even if one type is missing
    if 'TRANSFER_IN' not in summary.columns: summary['TRANSFER_IN'] = 0.0
    if 'TRANSFER_OUT' not in summary.columns: summary['TRANSFER_OUT'] = 0.0
    
    # Calculate the Delta
    summary['Net_Difference'] = summary['TRANSFER_IN'] - summary['TRANSFER_OUT']
    
    # Filter for assets where the transfer in/out does not balance
    anomalies = summary[summary['Net_Difference'].abs() > 0.01].sort_values(by='Net_Difference', ascending=False)
    
    if anomalies.empty:
        print("✅ All internal transfers are perfectly balanced!")
    else:
        print("🚨 MISMATCH DETECTED: The following assets have unbalanced transit volumes:\n")
        print(anomalies[['TRANSFER_IN', 'TRANSFER_OUT', 'Net_Difference']].to_string())
        print("\nFix Action: Check the raw CSVs for these specific assets. You may need to map an incoming corporate action to SPINOFF or SPLIT instead of TRANSFER_IN.")

if __name__ == "__main__":
    hunt_phantom_shares()