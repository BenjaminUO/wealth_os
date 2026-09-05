"""
WEALTH OS - FORENSIC QA AUDITOR
Uses the Gemini API (Flash Model) to perform high-speed, programmatic audits on 
raw transaction categorizations and ticker symbol mappings. 
Outputs a structured JSON-driven Markdown report of any detected anomalies.
"""

import os
import json
import time
import pandas as pd
from google import genai
from google.genai import types
from pathlib import Path

# Import Master Configurations
from src.config import (
    TRANSACTIONS_FILE, MAPPING_FILE, REPORTS_DIR
)

# ==========================================
# 1. TICKER MAPPING AUDITOR
# ==========================================

def audit_ticker_mappings(client: genai.Client) -> list:
    """
    Scans the ticker mapping dictionary to find mismatched or hallucinated tickers.
    Forces the AI to return a strict JSON array.
    """
    if not MAPPING_FILE.exists():
        return []

    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    # Filter out N/A and DELISTED to save tokens and focus the AI
    active_mappings = {
        asset: data.get("ticker") 
        for asset, data in mapping.items() 
        if data.get("ticker") and data.get("ticker") != "N/A"
    }

    if not active_mappings:
        return []

    print("\n🕵️ Auditing Ticker Mappings for API hallucinations...")

    # Define the strict JSON schema the AI MUST follow
    ticker_schema = {
        "type": "ARRAY",
        "description": "A list of identified ticker mismatches. Return an empty array [] if all mappings are perfect.",
        "items": {
            "type": "OBJECT",
            "properties": {
                "Asset": {"type": "STRING", "description": "The name of the asset"},
                "Current_Ticker": {"type": "STRING", "description": "The current ticker mapped in the system"},
                "Suggested_Ticker": {"type": "STRING", "description": "The correct ticker you suggest"},
                "Reason": {"type": "STRING", "description": "Why this mapping is objectively wrong"}
            },
            "required": ["Asset", "Current_Ticker", "Suggested_Ticker", "Reason"]
        }
    }

    prompt = f"""
    You are an elite financial data auditor. I am providing a JSON dictionary mapping Swedish/Global Asset Names to their Financial Tickers.
    Your mandate is to identify OBVIOUS mismatches or AI hallucinations. 
    
    RULES:
    1. Valid European cross-listings (e.g., FRA: for Germany, STO: for Sweden) are acceptable. Do not flag them.
    2. ONLY flag objective errors (e.g., 'Apple Inc' mapped to 'MSFT', or a large cap mapped to a random penny stock).
    3. If there are no errors, return an empty JSON array.
    
    MAPPINGS TO REVIEW:
    {json.dumps(active_mappings)}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0, # 0.0 guarantees maximum deterministic accuracy
                response_mime_type="application/json",
                response_schema=ticker_schema
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"      ⚠️ Ticker Audit Error: {e}")
        return []


# ==========================================
# 2. TRANSACTION CATEGORIZATION AUDITOR
# ==========================================

def process_transaction_batch(client: genai.Client, batch_df: pd.DataFrame, batch_number: int, total_batches: int) -> list:
    """
    Scans a batch of transactions using strict double-entry physics rules.
    """
    # Convert batch to a lightweight dictionary to minimize token usage
    records = batch_df[['Date', 'Original_Type', 'Standard_Type', 'Asset', 'Amount_SEK']].to_dict('records')

    # Define the strict JSON schema
    tx_schema = {
        "type": "ARRAY",
        "description": "A list of miscategorized transactions. Return an empty array [] if all follow the rules perfectly.",
        "items": {
            "type": "OBJECT",
            "properties": {
                "Date": {"type": "STRING"},
                "Asset": {"type": "STRING"},
                "Original_Type": {"type": "STRING", "description": "The raw bank string"},
                "Current_Type": {"type": "STRING", "description": "The current Standard_Type mapping"},
                "Suggested_Type": {"type": "STRING", "description": "The correct Standard_Type based on physics rules"},
                "Reason": {"type": "STRING", "description": "Which physics rule was violated"}
            },
            "required": ["Date", "Asset", "Original_Type", "Current_Type", "Suggested_Type", "Reason"]
        }
    }

    prompt = f"""
    You are an elite forensic financial data engineer. We are building a strict double-entry accounting ledger from raw Swedish broker exports.
    
    CRITICAL DOUBLE-ENTRY PHYSICS RULES YOU MUST OBEY:
    1. TRANSFER_IN and TRANSFER_OUT are strictly reserved for ASSET SHARES (Units), NEVER CASH.
    2. Cash moving between accounts (e.g., "Intern överföring", "Delåterköp", "Uttag") MUST be mapped to WITHDRAWAL or DEPOSIT.
    3. 0 SEK Redemptions ("Inlösen") MUST be mapped to SELL, not SPLIT.
    4. "Utdelning värdepapper" (Dividend paid in shares) MUST be mapped to TRANSFER_IN (to inject shares at 0 cost), not DIVIDEND.
    5. "Utbetalning aktielån" (Stock lending income) is safely mapped to DIVIDEND or INTEREST. Both are valid.
    6. "Uttag" is normally WITHDRAWAL, but if the asset is specifically "SAVRS FONDAVGIFT", it MUST be mapped to FEE to protect the cash balance.

    Review the following batch of transactions. ONLY flag a miscategorization if it explicitly violates these rules or is objectively illogical (e.g., a "Köp" mapped to DIVIDEND).

    BATCH DATA:
    {json.dumps(records)}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=tx_schema
            )
        )
        return json.loads(response.text)
    except Exception as e:
        if "503" in str(e) or "429" in str(e):
            print(f"      ⏳ API Rate Limit Hit. Sleeping for 10s...")
            time.sleep(10)
            raise e # Triggers the retry loop in the main function
        print(f"      🚨 Unexpected Batch Error: {e}")
        return []


# ==========================================
# 3. MASTER EXECUTION ORCHESTRATOR
# ==========================================

def run_qa_audit_agent():
    if not TRANSACTIONS_FILE.exists():
        print(f"🚨 CRITICAL ERROR: {TRANSACTIONS_FILE.name} not found.")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("🚨 CRITICAL ERROR: 'GEMINI_API_KEY' environment variable is missing.")
        return

    # Initialize the NEW SDK Client
    client = genai.Client(api_key=api_key)

    # --- PART 1: TICKER AUDIT ---
    ticker_errors = audit_ticker_mappings(client)
    if ticker_errors:
        print(f"   -> ⚠️ Found {len(ticker_errors)} potential Ticker Anomalies.")
    else:
        print("   -> ✅ All tickers appear to be logically sound.")

    # --- PART 2: TRANSACTION AUDIT ---
    df = pd.read_csv(TRANSACTIONS_FILE, keep_default_na=False)
    print(f"\n🕵️ Slicing {len(df)} transactions into AI processing batches...")
    
    # Batch size of 200 is optimal for the LLM context window to prevent attention drift
    batch_size = 350
    batches = [df.iloc[i:i + batch_size] for i in range(0, len(df), batch_size)]
    total_batches = len(batches)
    
    transaction_errors = []

    for i, batch in enumerate(batches):
        success = False
        retries = 3
        while not success and retries > 0:
            try:
                batch_errors = process_transaction_batch(client, batch, i + 1, total_batches)
                if batch_errors:
                    transaction_errors.extend(batch_errors)
                print(f"   -> Scanning Batch {i + 1}/{total_batches}... ✅ Clear")
                success = True
                time.sleep(1.5) # Graceful pacing to prevent 429 Too Many Requests
            except Exception:
                retries -= 1
                if retries == 0:
                    print(f"   -> ❌ Batch {i + 1} permanently failed after retries.")

    # --- PART 3: REPORT GENERATION ---
    print("\n=========================================================")
    print(f"✅ EXHAUSTIVE DATA QA SCAN COMPLETE.")
    print(f"   - Ticker Anomalies Found: {len(ticker_errors)}")
    print(f"   - Transaction Anomalies Found: {len(transaction_errors)}")
    print("=========================================================\n")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "QA_Data_Integrity_Audit.md"

    if ticker_errors or transaction_errors:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 🕵️ Master AI Data Integrity Audit Report\n\n")
            
            # Write Ticker Errors
            if ticker_errors:
                f.write("## ⚠️ TICKER MAPPING ANOMALIES\n")
                f.write("> **ACTION REQUIRED:** If the AI is correct, update `MANUAL_TICKER_OVERRIDES` in `src/config.py`.\n\n")
                for err in ticker_errors:
                    f.write(f"### 🎯 Asset: {err.get('Asset', 'Unknown')}\n")
                    f.write(f"- **Current Ticker:** ❌ `{err.get('Current_Ticker', 'N/A')}`\n")
                    f.write(f"- **Suggested Ticker:** ✅ `{err.get('Suggested_Ticker', 'N/A')}`\n")
                    f.write(f"- **AI Reasoning:** {err.get('Reason', 'No reason provided.')}\n\n")
                f.write("---\n\n")

            # Write Transaction Errors
            if transaction_errors:
                f.write("## ⚠️ TRANSACTION CATEGORIZATION ANOMALIES\n")
                f.write("> **ACTION REQUIRED:** If correct, update the `TRANSACTION_TYPE_MAPPING` dictionary in `src/config.py`.\n\n")
                for err in transaction_errors:
                    f.write(f"### 📅 {err.get('Date', 'Unknown Date')} | {err.get('Asset', 'Unknown Asset')}\n")
                    f.write(f"- **Bank Raw Label:** `{err.get('Original_Type', 'N/A')}`\n")
                    f.write(f"- **Current Script Label:** ❌ `{err.get('Current_Type', 'N/A')}`\n")
                    f.write(f"- **AI Suggested Label:** ✅ `{err.get('Suggested_Type', 'N/A')}`\n")
                    f.write(f"- **AI Reasoning:** {err.get('Reason', 'No reason provided.')}\n\n")

        print(f"💾 Findings securely saved to '{REPORTS_DIR.name}/{report_path.name}'. Please review and update config.py if necessary.")
    else:
        print("🎉 Zero anomalies found! Your raw data ingestion rules are pristine.")
        # Wipe the old report if it exists so you know it's currently clean
        if report_path.exists():
            report_path.unlink()

if __name__ == "__main__":
    run_qa_audit_agent()