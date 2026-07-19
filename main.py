"""
WEALTH OS - MASTER ORCHESTRATOR
Executes the deterministic financial engine in strict chronological order.
Passes DataFrames through memory to maximize execution speed and eliminate I/O lag.
"""

import argparse
import time
from dotenv import load_dotenv

# Core Data Pipeline
from src.cleaner import clean_and_merge_transactions
from src.scraper import generate_ticker_mapping, update_missing_prices
from src.ledger import generate_portfolio
from src.validator import run_validation_agent
from src.portfolio_metrics import run_metrics_and_viz
from src.historical_analyzer import run_historical_backtest
from src.audit_transfers import hunt_phantom_shares

# Optional AI Modules
from src.qa_agent import run_qa_audit_agent
from src.cio_agent import run_portfolio_agent


def ask_yes_no(question: str, default: bool = False) -> bool:
    """Provides an interactive CLI prompt for optional AI executions."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{question} ({default_str}): ").strip().lower()
    if not response:
        return default
    return response[0] == "y"


def main():
    # Setup the argument parser for automated cloud/cron executions
    parser = argparse.ArgumentParser(description="Wealth OS Financial Engine")
    parser.add_argument("--validate", action="store_true", help="Run the deterministic validation agent")
    parser.add_argument("--audit-transfers", action="store_true", help="Run the phantom transfer audit")
    parser.add_argument("--qa", action="store_true", help="Run the Gemini QA Audit Agent")
    parser.add_argument("--advisor", action="store_true", help="Run the Gemini CIO Portfolio Agent")
    parser.add_argument("--auto", action="store_true", help="Run all optional manual agents silently")
    args = parser.parse_args()

    # Load environment variables (API Keys)
    load_dotenv()

    print("🚀 Starting Wealth OS Engine...")
    start_time = time.time()

    # ==========================================
    # CORE PIPELINE (In-Memory Execution)
    # ==========================================
    
    print("\n--- STEP 1: Processing Raw Bank Data ---")
    transactions_df = clean_and_merge_transactions()
    if transactions_df is None or transactions_df.empty:
        print("🚨 Pipeline aborted at Step 1: No valid transactions parsed. Check your data/raw/ folder.")
        return

    print("\n--- STEP 2: Updating Market Data ---")
    generate_ticker_mapping()
    update_missing_prices()

    print("\n--- STEP 3: Compiling Double-Entry Ledger ---")
    portfolio_df = generate_portfolio(transactions_df)
    if portfolio_df is None or portfolio_df.empty:
        print("🚨 Pipeline aborted at Step 3: Ledger compilation failed.")
        return

    run_validation = args.auto or args.validate or ask_yes_no("\n🛡️ Run deterministic validation agent?", default=False)
    if run_validation:
        print("\n--- STEP 4: Deterministic Validation & GF Tick Check ---")
        verified_df = run_validation_agent(portfolio_df, transactions_df)
        if verified_df is None or verified_df.empty:
            print("🚨 Pipeline aborted at Step 4: Deterministic Validation failed.")
            return
    else:
        print("\n--- STEP 4: Skipping deterministic validation agent (run with --validate to enable).")
        verified_df = portfolio_df

    print("\n--- STEP 5: Generating Live Metrics & Visualizations ---")
    metrics_df = run_metrics_and_viz(verified_df)
    if metrics_df is None or metrics_df.empty:
        print("🚨 Pipeline aborted at Step 5: Metrics generation failed.")
        return

    print("\n--- STEP 6: Historical Backtesting & Benchmarking ---")
    # Runs last so it inherits any 404 ticker fixes made by the Validator in Step 4
    run_historical_backtest()

    run_transfer_audit = args.auto or args.audit_transfers or ask_yes_no("\n🕵️ Run phantom transfer audit?", default=False)
    if run_transfer_audit:
        print("\n--- STEP 7: Auditing Internal Transfers for Phantom Shares ---")
        hunt_phantom_shares()
    else:
        print("\n--- STEP 7: Skipping phantom transfer audit (run with --audit-transfers to enable).")

    # ==========================================
    # AI INTELLIGENCE PIPELINE
    # ==========================================

    # QA Audit Agent (Scans Transactions & Tickers)
    if args.auto or args.qa or ask_yes_no("\n🤖 Run Forensic QA Audit Agent?", default=False):
        run_qa_audit_agent()

    # CIO Portfolio Agent (Scans Net Worth & Asset Weights)
    if args.auto or args.advisor or ask_yes_no("\n🏛️ Run CIO Portfolio Agent?", default=False):
        run_portfolio_agent()

    elapsed = round(time.time() - start_time, 2)
    print(f"\n✅ Pipeline Complete in {elapsed} seconds!")


if __name__ == "__main__":
    main()