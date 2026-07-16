🚀 WEALTH OS v2.0

A Deterministic, High-Performance Financial Tracking \& Backtesting Engine



🎯 Project Vision \& Goals

The fundamental goal of WEALTH OS is to construct an absolute, mathematically perfect historical timeline of a user's net worth, immune to the chaotic, fragmented data formats of modern brokerages.



Standard portfolio trackers rely on static, point-in-time snapshots that fail when assets merge, delist, or transfer between banks. WEALTH OS solves this by treating personal finance like Physics. It replays every transaction chronologically from "Day 0" using strict Double-Entry Accounting principles. Matter (cash and units) cannot be created or destroyed, only transferred.



This architecture is a living foundation. It is specifically designed to be highly adaptable. As new brokers, edge cases, asset classes, and transaction types emerge, the engine is built to be easily expanded and improved.



Core Objectives:



Sanitize Chaos: Ingest raw, messy CSV exports from diverse brokerages and dynamically normalize a constantly growing array of transaction terms into a unified set of double-entry accounting categories.



Deterministic Accuracy: Calculate exact Cost Basis (GAV), realized gains, and historical ROI, entirely resilient to timezone anomalies, missing broker data, and API rate limits.



Institutional Insights: Generate interactive, institutional-grade Plotly dashboards combining listed equities, OTC assets, and unlisted mutual funds into a single, cohesive view.



⚙️ The Full Execution Pipeline

The system operates as an extremely fast, Pandas-based in-memory pipeline. To eliminate I/O lag, DataFrames are passed physically through memory from one module to the next, only writing to disk at the end of major processing steps for auditing.



Ingestion \& Neutralization: The engine reads raw broker CSVs. It vaporizes canceled trades, intercepts broken corporate actions, and unifies fragmented stock ISINs.



Market Mapping: It pings financial APIs (like Yahoo Finance) and private mutual fund backends to establish a cached "brain" (ticker\_mapping.json), mapping every asset to a live ticker or fallback NAV price.



The Physics Engine (Ledger): The engine steps through time day-by-day. It moves units and SEK cash between assets, calculates dilution during spinoffs, and handles transit vaults for broker-to-broker transfers.



Validation: A strict QA agent audits the ledger to ensure no fractional dust was left behind, no phantom money was printed, and no duplicate rows slipped through.



Live Valuation: The engine executes chunked, asynchronous batch calls for live market prices. It applies live FX conversions natively and utilizes Absolute Cost-Basis Fallbacks if network requests fail.



Visualization: Generates dynamic, interactive HTML dashboards (Heatmaps, Bubble Charts, Donuts) to visualize asset allocation, risk/reward, and lifetime profit generators.



🗂️ The Codebase (Module Breakdown)

Every script in the src/ directory has a highly specific, isolated responsibility.



main.py (The Master Orchestrator)

The conductor of the pipeline. It sequences the execution of all other scripts, passing the Pandas DataFrames seamlessly through memory from ingestion all the way to final HTML generation.



src/config.py (The Master Switchboard)

The absolute source of truth for how the engine interprets reality. It contains the translation dictionaries for banking terms, manual ticker overrides to bypass API bugs, asset rename rules to merge fragmented corporate actions, and broker ingestion schemas. Because banks frequently change their formats, adaptability lives here. If the engine misinterprets an asset, it is fixed in this config, not in the core logic scripts.



src/utils.py (The Math \& Network Backbone)

Handles the rigorous formatting required before financial math can be executed.



Uses pure raw string regex to annihilate hard-spaces and European commas in numbers.



Contains a highly optimized, @lru\_cached FX engine that handles historical exchange rates with "Timezone Poisoning Shields" to prevent Pandas index crashes.



Resolves international currency anomalies natively.



src/cleaner.py (The Artifact Nullifier)

Responsible for reading the raw CSVs and transforming them into a unified format. It houses specialized, adaptable heuristics:



The Makulerad Shield: Vaporizes canceled broker trades before they enter the system.



Broker Interceptors: Catches fragmented or manual corporate actions (e.g., missing cash rows or unlogged conversions) and routes them into standard Buy/Sell/Transfer mechanics.



Safe Split Heuristic: Differentiates between a legitimate 1:1 stock transfer to a new broker and an actual stock split.



src/scraper.py (The Brain Builder)

Connects to external APIs and establishes the global ticker\_mapping.json cache. This prevents the system from repeatedly pinging the web for static asset information, ensuring rate limits are respected.



src/ledger.py (The Physics Engine)

The double-entry accounting core. It processes the cleaned data chronologically, adhering to thermodynamic laws of finance.



The Transit Vault: Remembers historical Cost Basis when shares are transferred between brokers so the ROI denominator doesn't artificially reset to zero.



Spinoff Dilution: Injects units without adding cash to the cost basis, naturally diluting the asset's GAV.



Fractional Dust Sweeper: Cleans up floating-point math errors (e.g., 0.0000001 shares) and sweeps residual values into the Historical Cost Sold vault to prevent memory leaks.



src/portfolio\_metrics.py (Live Valuation \& Visualization)

Calculates real-time market value and constructs the UI.



Uses chunked, async batch calls to prevent HTTP 429 Rate Limits from market data providers.



Absolute Valuation Fallback: If an external API drops a ticker or goes offline, it explicitly values the asset at its Average Buy Price so the portfolio's total Net Worth doesn't artificially crash.



Generates the final, interactive Plotly HTML dashboards.



src/validator.py (The QA Agent)

A deterministic auditing script that runs math checks on the final ledger, ensuring total cash in minus total cash out equals the current system state.



src/historical\_analyzer.py (The Time Machine)

Calculates daily interpolations of the portfolio's historical value against benchmark indices, generating a continuous historical equity curve for long-term backtesting.



src/qa\_agent.py \& src/cio\_agent.py (AI Forensics)

Modular AI extensions that feed the sanitized DataFrames directly into an LLM (like Google's Gemini) for forensic auditing and automated Chief Investment Officer allocation advice.



⚠️ Critical Maintenance Rules (For Future Developers)

The JSON Cache Trap: The scraper.py script generates data/processed/ticker\_mapping.json. This file acts as the system's memory bank. If you ever update config.py (e.g., adding a new ticker override or rename rule), you MUST manually delete ticker\_mapping.json before running the engine. Otherwise, the system will prioritize the old cache and ignore your new code.



Aggressive Regex is Banned: Do not use blanket .replace() regex to clean asset names in cleaner.py. Banks frequently reuse words (e.g., "Nordnet" the stock vs. "Nordnet AB" the fund). Use exact string matching in config.py's ASSET\_RENAME\_RULES to maintain precise control.



Handling Unlisted / Ghost Assets: If an asset is private, bankrupt, or unlisted, map it to "N/A" in config.py's MANUAL\_TICKER\_OVERRIDES. This ensures the engine bypasses external network checks entirely, preventing pipeline crashes.

