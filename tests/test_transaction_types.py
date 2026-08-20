import pandas as pd
import sys
from pathlib import Path

# Add project root to sys.path to import config safely
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from src.config import TRANSACTION_TYPE_MAPPING
except ImportError:
    TRANSACTION_TYPE_MAPPING = {}

def load_broker_csv(filepath: Path):
    name = filepath.name.lower()
    if "transactions-and-notes" in name or "nordnet" in name:
        df = pd.read_csv(filepath, sep='\t', encoding='utf-16', dtype=str)
        bank = "Nordnet"
        type_col = 'Transaktionstyp'
        acc_col = 'Depå'
    elif "transaktioner_20" in name or "avanza" in name:
        df = pd.read_csv(filepath, sep=';', encoding='utf-8-sig', dtype=str)
        bank = "Avanza"
        type_col = 'Typ av transaktion'
        acc_col = 'Konto'
    elif "savr" in name:
        df = pd.read_csv(filepath, sep=';', encoding='utf-8-sig', dtype=str)
        bank = "SAVR"
        type_col = 'Transaktionstyp'
        acc_col = 'Konto'
    else:
        df = pd.read_csv(filepath, sep=',', encoding='utf-8-sig', dtype=str)
        bank = "Montrose"
        type_col = 'Typ'
        acc_col = 'Konto'
    return df, bank, type_col, acc_col

def run_type_audit():
    raw_dir = Path('data/raw')
    if not raw_dir.exists(): raw_dir = Path('../data/raw')
    
    files = list(raw_dir.glob('*.csv'))
    if not files:
        print(f"❌ No raw CSV files found in '{raw_dir}'")
        return

    print("\n" + "="*105)
    print(" 📋 WEALTH OS - RAW TRANSACTION TYPE BREAKDOWN & LEXICON AUDIT")
    print("="*105)
    
    unmapped_found = []
    
    for f in files:
        df, bank, type_col, acc_col = load_broker_csv(f)
        if type_col not in df.columns:
            continue
            
        print(f"\n📂 BROKER: {bank} (File: {f.name})")
        print("-" * 75)
        
        # Group by account and raw transaction type
        grouped = df.groupby([acc_col, type_col]).size().reset_index(name='Count')
        grouped.columns = ['Account', 'Raw_Type', 'Count']
        
        for _, row in grouped.iterrows():
            acc = row['Account']
            raw_t = str(row['Raw_Type']).strip()
            cnt = row['Count']
            
            std_type = TRANSACTION_TYPE_MAPPING.get(raw_t.upper(), '⚠️ UNMAPPED')
            status = "✅" if std_type != '⚠️ UNMAPPED' else "🚨"
            
            if std_type == '⚠️ UNMAPPED':
                unmapped_found.append((bank, acc, raw_t))
                
            print(f" {status} [{str(acc).ljust(22)}] {raw_t.ljust(35)} -> {std_type.ljust(15)} (x{cnt})")

    print("\n" + "="*105)
    if unmapped_found:
        print("🚨 UNMAPPED TRANSACTION TYPES DETECTED (These get dropped into 'OTHER'):")
        for bank, acc, raw_t in set(unmapped_found):
            print(f"   - Broker: {bank} | Account: {acc} | Raw String: '{raw_t}'")
        print("👉 Fix: Add these strings to TRANSACTION_TYPE_MAPPING in 'src/config.py'.")
    else:
        print("✅ ALL RAW TRANSACTION TYPES ARE FULLY MAPPED IN CONFIG.PY!")
    print("="*105 + "\n")

if __name__ == "__main__":
    run_type_audit()