import pandas as pd
from pathlib import Path

def resolve_path(rel_path: str) -> Path:
    p = Path(rel_path)
    if p.exists(): return p
    p_up = Path("..") / rel_path
    if p_up.exists(): return p_up
    return p

def calculate_deposit_summary(df: pd.DataFrame) -> tuple[float, float, float]:
    total_deposits = df.loc[df['Standard_Type'] == 'DEPOSIT', 'Amount_SEK'].sum()
    total_withdrawals = df.loc[df['Standard_Type'] == 'WITHDRAWAL', 'Amount_SEK'].sum()
    total_net_deposits = total_deposits - total_withdrawals

    print(f"Total deposits: {total_deposits:,.2f} SEK")
    print(f"Total withdrawals: {total_withdrawals:,.2f} SEK")
    print(f"Total net deposits: {total_net_deposits:,.2f} SEK")

    return total_deposits, total_withdrawals, total_net_deposits

def run_cash_test():
    tx_file = resolve_path('data/processed/combined_transactions.csv')
    if not tx_file.exists():
        print(f"❌ Error: Could not find '{tx_file}'. Please run cleaner.py / main.py first.")
        return

    df = pd.read_csv(tx_file)
    df['Amount_SEK'] = pd.to_numeric(df['Amount_SEK'], errors='coerce').fillna(0.0).abs()
    calculate_deposit_summary(df)
    
    results = []
    grouped = df.groupby(['Bank', 'Account'])
    
    for (bank, account), group in grouped:
        deposits = group[group['Standard_Type'] == 'DEPOSIT']['Amount_SEK'].sum()
        withdrawals = group[group['Standard_Type'] == 'WITHDRAWAL']['Amount_SEK'].sum()
        buys = group[group['Standard_Type'] == 'BUY']['Amount_SEK'].sum()
        sells = group[group['Standard_Type'] == 'SELL']['Amount_SEK'].sum()
        dividends = group[group['Standard_Type'] == 'DIVIDEND']['Amount_SEK'].sum()
        interest = group[group['Standard_Type'] == 'INTEREST']['Amount_SEK'].sum()
        taxes = group[group['Standard_Type'] == 'TAX']['Amount_SEK'].sum()
        taxes_refund = group[group['Standard_Type'] == 'TAX_REFUND']['Amount_SEK'].sum()
        fees = group[group['Standard_Type'] == 'FEE']['Amount_SEK'].sum()

        cash_in = deposits + sells + dividends + interest + taxes_refund
        cash_out = withdrawals + buys + taxes + fees
        net_cash = cash_in - cash_out
        
        results.append({
            'Bank': bank,
            'Account': str(account),
            'Net Cash (SEK)': round(net_cash, 2),
            'Cash IN': round(cash_in, 2),
            'Cash OUT': round(cash_out, 2),
            'Deposits': round(deposits, 2),
            'Withdrawals': round(withdrawals, 2),
            'Buys': round(buys, 2),
            'Sells': round(sells, 2),
            'Dividends': round(dividends, 2),
            'Taxes': round(taxes, 2),
            'Fees': round(fees, 2)
        })

    audit_df = pd.DataFrame(results).sort_values('Net Cash (SEK)', ascending=False)
    
    print("\n" + "="*115)
    print(" 💵 WEALTH OS - CASH LEDGER AUDIT BY BROKER & ACCOUNT")
    print("="*115)
    print(audit_df.to_string(index=False))
    print("-" * 115)
    total_cash = audit_df['Net Cash (SEK)'].sum()
    print(f"💰 Global System Cash: {total_cash:,.2f} SEK")
    print("=" * 115 + "\n")

if __name__ == "__main__":
    run_cash_test()