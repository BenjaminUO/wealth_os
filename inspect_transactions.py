from src.cleaner import clean_and_merge_transactions
import pandas as pd

df = clean_and_merge_transactions()
print('COLUMNS:', df.columns.tolist())
mask = df['Asset'].astype(str).str.contains('ELECTROLUX|BTA|VERISURE|ZAP|SCATC|AVANT|EXPI|CSPX', case=False, na=False)
print('MATCH COUNT', mask.sum())
print(df.loc[mask, ['Date', 'Original_Type', 'Asset', 'ISIN', 'Quantity', 'Amount_SEK']].head(120).to_string(index=False))
