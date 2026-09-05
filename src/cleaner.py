"""
WEALTH OS - INGESTION & STANDARDIZATION ENGINE
Consumes chaotic, fragmented CSV exports from Swedish brokers,
enforces strict formatting, and outputs a chronologically perfect Pandas DataFrame.
"""
import pandas as pd
import numpy as np
import os

# Import Master Configurations and Utilities
from src.config import (
    RAW_DIR, TRANSACTIONS_FILE, BROKER_PROFILES, 
    TRANSACTION_TYPE_MAPPING, MANUAL_NAME_OVERRIDES, 
    ASSET_RENAME_RULES, CASH_TYPES
)
from src.utils import clean_swedish_numbers

def clean_and_merge_transactions() -> pd.DataFrame:
    """
    Scans the raw data directory, unifies broker formats, applies accounting rigor,
    and returns a pristine, mathematically sound DataFrame.
    """
    if not RAW_DIR.exists():
        print(f"🚨 CRITICAL ERROR: Directory '{RAW_DIR}' missing. Please create it and add bank CSVs.")
        return pd.DataFrame()

    dataframes = []
    print(f"\n🔍 Scanning '{RAW_DIR}' for financial export files...")

    # ==========================================
    # 1. DYNAMIC FILE DISCOVERY & INGESTION
    # ==========================================
    for file_path in RAW_DIR.glob('*.csv'):
        filename = file_path.name
        lower_name = filename.lower()
        bank = None

        # Intelligent keyword detection mapping
        if "transactions-and-notes" in lower_name or "nordnet" in lower_name:
            bank = "Nordnet"
        elif "transaktioner_20" in lower_name or "avanza" in lower_name:
            bank = "Avanza"
        elif "savr" in lower_name:
            bank = "SAVR"
        elif "transaktioner" in lower_name:
            bank = "Montrose"
        elif "manual" in lower_name:
            bank = "Manual"

        if bank:
            print(f"   -> 📂 Ingesting {bank} file: '{filename}'")
            profile = BROKER_PROFILES[bank]
            
            try:
                # Provide on_bad_lines="warn" to prevent pandas from skipping perfectly valid trades
                df = pd.read_csv(file_path, sep=profile["sep"], encoding=profile["encoding"], dtype=str, on_bad_lines="warn")
            except (UnicodeError, pd.errors.ParserError):
                # Emergency fallback if Nordnet changes their export encoding or uses a bad BOM
                fallback_enc = "utf-8-sig" if profile["encoding"] == "utf-16" else "utf-16"
                try:
                    df = pd.read_csv(file_path, sep=profile["sep"], encoding=fallback_enc, dtype=str, on_bad_lines="warn")
                except Exception:
                    # Absolute last resort for corrupted Nordnet exports
                    df = pd.read_csv(file_path, sep='\t', encoding='utf-16', dtype=str, on_bad_lines="warn")

            # ========================================================
            # 🛡️ THE SAVR CORPORATE ACTION INTERCEPTOR
            # Must happen here BEFORE column renaming
            # ========================================================
            if bank == 'SAVR' and 'Värdepapper/transaktionsnamn' in df.columns:
                # Target the exact raw Swedish strings
                is_savr_anomaly = (df['Värdepapper/transaktionsnamn'] == 'Bolagshändelse') & (df['Transaktionstyp'] == 'Betalning')
                
                # Re-route the asset to Intrum and force it to be a BUY of 0 units
                df.loc[is_savr_anomaly, 'Värdepapper/transaktionsnamn'] = 'Intrum'
                df.loc[is_savr_anomaly, 'Transaktionstyp'] = 'Köp'
                df.loc[is_savr_anomaly, 'Antal'] = '0'
            # ========================================================
            
            # --- THE MAKULERAD SHIELD ---
            # Scan ALL raw columns for "makuler" (canceled trades) before dropping any data
            mask_makulerad = df.apply(lambda row: row.astype(str).str.contains('makuler', case=False, na=False).any(), axis=1)
            canceled_count = mask_makulerad.sum()
            if canceled_count > 0:
                print(f"      🛡️  Shield Activated: Vaporized {canceled_count} canceled/makulerad trades.")
                df = df[~mask_makulerad].copy()

            # Map fields safely according to the config profile
            available_cols = {raw_col: std_col for raw_col, std_col in profile["cols"].items() if raw_col in df.columns}
            df = df[list(available_cols.keys())].rename(columns=available_cols)
            df['Bank'] = bank

            # Ensure all standard columns exist to prevent downstream KeyErrors
            if 'Fee' not in df.columns: df['Fee'] = '0.0'
            if 'Quantity' not in df.columns: df['Quantity'] = '0.0'
            if 'Price' not in df.columns: df['Price'] = '0.0'
            if 'Amount_SEK' not in df.columns: df['Amount_SEK'] = '0.0'
            if 'ISIN' not in df.columns: df['ISIN'] = ''
            if 'Account' not in df.columns: df['Account'] = 'Unknown'

            # Save the exact string the bank used for auditing purposes
            df['Original_Type'] = df['Type']

            dataframes.append(df)
        else:
            print(f"   -> ⚠️ Skipped unrecognized file: '{filename}'")

    if not dataframes:
        print("❌ Error: No valid brokerage dataframes could be parsed. Check your raw folder.")
        return pd.DataFrame()

    # Combine all bank records into the master timeline
    df_all = pd.concat(dataframes, ignore_index=True)


    # ==========================================
    # 2. STRING, NUMBER & DATE SANITIZATION
    # ==========================================
    print("🧹 Sanitizing numerical artifacts and standardizing dates...")
    
    # Execute the vectorized utility cleaner on numerical strings
    for col in ['Quantity', 'Price', 'Amount_SEK', 'Fee']:
        df_all[col] = clean_swedish_numbers(df_all[col])

        # Enforce strict ISO-8601 date formatting
    df_all['Date'] = pd.to_datetime(df_all['Date'].astype(str).str.slice(0, 10), format='%Y-%m-%d', errors='coerce')
    
    # --- ADD THE SILENT DATA LOSS ALARM ---
    invalid_dates = df_all[df_all['Date'].isna()]
    if not invalid_dates.empty:
        print(f"  [CRITICAL WARNING] Dropping {len(invalid_dates)} rows due to unparseable dates. Check raw CSV format changes.")
    
    df_all = df_all.dropna(subset=['Date'])
    
    df_all['Asset'] = df_all['Asset'].astype(str).str.strip()
    df_all['ISIN'] = df_all['ISIN'].astype(str).str.strip().replace('nan', '')

    print("⚖️ Forcing bank terms into Double-Entry Accounting categories...")
    df_all['Standard_Type'] = df_all['Original_Type'].astype(str).str.upper().map(TRANSACTION_TYPE_MAPPING).fillna('OTHER')

    # ==========================================
    # 4. ASSET UNIFICATION (ISIN & NAME)
    # ==========================================
    print("🔗 Unifying fragmented broker asset names via ISIN matching...")

    # A. Override specific broken ISINs directly from config
    df_all['Asset'] = df_all.apply(
        lambda row: MANUAL_NAME_OVERRIDES[row['ISIN']] if row['ISIN'] in MANUAL_NAME_OVERRIDES else row['Asset'],
        axis=1
    )

    # B. Auto-group assets by ISIN to find the most common name
    valid_isins = df_all[df_all['ISIN'] != '']
    isin_to_name = valid_isins.groupby('ISIN')['Asset'].agg(lambda x: x.value_counts().index[0]).to_dict()

    df_all['Asset'] = df_all.apply(
        lambda row: isin_to_name[row['ISIN']] if row['ISIN'] in isin_to_name else row['Asset'],
        axis=1
    )

    # C. Strip specific string pollution ("UTDELNING ", etc.)
    df_all['Asset'] = df_all['Asset'].str.replace(r'^UTDELNING ', '', regex=True)
    df_all['Asset'] = df_all['Asset'].str.replace(r'^UTLÄNDSK KÄLLSKATT ', '', regex=True)
    
    # D. Safely map specific artifact names via the surgical ASSET_RENAME_RULES matrix
    df_all['Asset'] = df_all['Asset'].replace(ASSET_RENAME_RULES)


    # ==========================================
    # 5. DIRECTIONALITY & HEURISTIC FIXES
    # ==========================================
    df_all.loc[(df_all['Standard_Type'] == 'DEPOSIT') & (df_all['Amount_SEK'] < 0), 'Standard_Type'] = 'WITHDRAWAL'
    df_all.loc[(df_all['Standard_Type'] == 'WITHDRAWAL') & (df_all['Amount_SEK'] > 0), 'Standard_Type'] = 'DEPOSIT'
    df_all.loc[(df_all['Standard_Type'] == 'TAX') & (df_all['Amount_SEK'] > 0), 'Standard_Type'] = 'TAX_REFUND'
    df_all.loc[(df_all['Standard_Type'] == 'FEE') & (df_all['Amount_SEK'] > 0), 'Standard_Type'] = 'DEPOSIT'
    df_all.loc[(df_all['Standard_Type'] == 'TRANSFER_IN') & (df_all['Quantity'] < 0), 'Standard_Type'] = 'TRANSFER_OUT'
    
    # --- THE STRICT ACCOUNTING FIXES (REVERSAL SHIELD) ---
    # 1. Canceled SELLs: Broker takes back cash (Amount_SEK < 0). Map to BUY to deduct cash and restore units.
    df_all.loc[(df_all['Standard_Type'] == 'SELL') & (df_all['Amount_SEK'] < 0), 'Standard_Type'] = 'BUY'
    
    # 2. Canceled BUYs: Broker refunds cash (Amount_SEK > 0). Map to SELL to add cash back and remove units.
    df_all.loc[(df_all['Standard_Type'] == 'BUY') & (df_all['Amount_SEK'] > 0), 'Standard_Type'] = 'SELL'
    
    # 3. Canceled DIVIDENDS: Broker takes back cash (Amount_SEK < 0). Map to TAX to deduct cash and correct Net Dividends.
    df_all.loc[(df_all['Standard_Type'] == 'DIVIDEND') & (df_all['Amount_SEK'] < 0), 'Standard_Type'] = 'TAX'
    
    # Vaporize broker ghost assets
    df_all = df_all[df_all['Asset'] != 'IGNORE_ASSET']

    # 3. THE STRICT DOUBLE-DIP ANNIHILATOR
    redundant_mask = (
        (df_all['Standard_Type'] == 'TRANSFER_OUT') & 
        (df_all['Original_Type'].str.upper().isin(['AVSKILJNING', 'INLÖSEN UTTAG VP', 'RENSNING UTTAG VP'])) &
        (df_all.duplicated(subset=['Date', 'Asset'], keep=False))
    )
    double_dip_count = redundant_mask.sum()
    if double_dip_count > 0:
        print(f"      🛡️  Strict Accounting Shield: Vaporized {double_dip_count} double-dipped broker transactions.")
    df_all = df_all[~redundant_mask]

    # 4. THE SAVR INTRUM TR BLACKLIST
    # SAVR failed to provide the deposit transaction for Intrum TRs, meaning processing their
    # withdrawal pushes the ledger into negative units. We strictly quarantine their broken data.
    savr_intrum_mask = (df_all['Bank'] == 'SAVR') & (df_all['Asset'] == 'INTRUM AB TR')
    df_all = df_all[~savr_intrum_mask]

    # Strict SAVR override (Protect the cash pool from pseudo-deposits)
    df_all.loc[df_all['Asset'].astype(str).str.upper() == 'SAVRS FONDAVGIFT', 'Standard_Type'] = 'FEE'
    
    df_all = df_all[df_all['Standard_Type'] != 'OTHER']

    # --- THE SAFE SPLIT VS TRANSFER HEURISTIC FIX ---
    # Only converts to SPLIT if the Out/In quantities are structurally different!
    # This prevents the heuristic from corrupting legitimate 1:1 broker transfers.
    split_candidates = df_all[df_all['Standard_Type'].isin(['TRANSFER_IN', 'TRANSFER_OUT'])]
    grouped = split_candidates.groupby(['Date', 'Asset'])
    
    for name, group in grouped:
        if 'TRANSFER_IN' in group['Standard_Type'].values and 'TRANSFER_OUT' in group['Standard_Type'].values:
            in_qty = group[group['Standard_Type'] == 'TRANSFER_IN']['Quantity'].abs().sum()
            out_qty = group[group['Standard_Type'] == 'TRANSFER_OUT']['Quantity'].abs().sum()
            
            # If the incoming units DO NOT EQUAL the outgoing units, it is a stock split
            if abs(in_qty - out_qty) > 0.01:
                mask = (df_all['Date'] == name[0]) & (df_all['Asset'] == name[1]) & (df_all['Standard_Type'].isin(['TRANSFER_IN', 'TRANSFER_OUT']))
                df_all.loc[mask, 'Standard_Type'] = 'SPLIT'

    # --- CASH SWEEP RECONCILIATION ---
    # Convert all deposits, withdrawals, and pure cash taxes/fees into the master 'SEK CASH' asset
    df_all.loc[df_all['Standard_Type'].isin(CASH_TYPES), 'Asset'] = 'SEK CASH'
    df_all.loc[df_all['Standard_Type'].isin(CASH_TYPES), 'ISIN'] = ''
    
    # Ensure raw fees not tied to a specific stock (e.g. account fees) hit the cash pool
    df_all.loc[(df_all['Standard_Type'].isin(['TAX', 'FEE', 'TAX_REFUND'])) & ((df_all['ISIN'] == '') | (df_all['ISIN'].isna())), 'Asset'] = 'SEK CASH'
    df_all.loc[df_all['Asset'] == 'SEK CASH', 'ISIN'] = ''

    # Remove any rogue artifact rows that lack an ISIN but claim to be stock buys/sells
    df_all = df_all[~((df_all['ISIN'] == '') & (df_all['Standard_Type'].isin(['BUY', 'SELL'])))]


    # ==========================================
    # 6. CHRONOLOGICAL SORT & CALIBRATION
    # ==========================================
    df_all = df_all.sort_values(['Date', 'Bank']).reset_index(drop=True)

    # Establish the initial Day 0 cash calibration anchor
    calibration_row = pd.DataFrame([{
        'Date': pd.to_datetime('2019-09-01'), 'Bank': 'System', 'Account': 'Calibration',
        'Standard_Type': 'WITHDRAWAL', 'Original_Type': 'Initial Cash Calibration',
        'Asset': 'SEK CASH', 'ISIN': '', 'Quantity': 0.0, 'Price': 0.0, 'Fee': 0.0, 'Amount_SEK': 0.0
    }])

    df_all = pd.concat([calibration_row, df_all], ignore_index=True)

    # Final column ordering
    final_cols = ['Date', 'Bank', 'Account', 'Standard_Type', 'Original_Type', 'Asset', 'ISIN', 'Quantity', 'Price', 'Fee', 'Amount_SEK']
    df_all = df_all[final_cols]


    # ==========================================
    # 7. OUTPUT TO SYSTEM
    # ==========================================
    # Save cleanly to data/processed/ for human auditing
    df_all.to_csv(TRANSACTIONS_FILE, index=False, encoding='utf-8-sig')
    print(f"✨ Success! {len(df_all)} standardized transactions ingested and saved.")
    
    # Return the dataframe directly to keep the pipeline moving in memory
    return df_all

if __name__ == "__main__":
    # If run directly for testing purposes
    clean_and_merge_transactions()