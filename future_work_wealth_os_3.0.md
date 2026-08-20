Wealth OS - Future Development Roadmap \& Technical Brief (v3.0)

To the Developer/Consultant: Wealth OS is a strict double-entry financial physics engine written in Python. It ingests raw Swedish brokerage exports (Avanza, Nordnet, SAVR, Montrose), standardizes transactions, reconstructs a chronological ledger to compute true cost basis, scrapes live/historical Net Asset Values (NAVs) for mutual funds, and benchmarks portfolio growth against the S\&P 500.

When implementing the phases below, do not modify or bypass the core accounting physics:

The Double-Dip Annihilator in cleaner.py.

The Strict Zero-Floor and Absolute Value Shields in ledger.py.

The Intra-Day Causality Order in ledger.py and historical\_analyzer.py.

Phase 1: Master Portfolio Aggregation Row

Problem: Google\_Sheets\_Live\_Portfolio.csv lists individual holdings but lacks a single bottom-line "Total" row.

Requirements:

Summary Calculation (ledger.py): Calculate portfolio-wide totals for Invested Capital, Current Value, Realized Gains, and Net Dividends.

True Portfolio ROI: Compute global ROI as $\\frac{\\text{Total Profit}}{\\text{Total Invested Capital}}$ rather than averaging individual asset percentages.

Export Formatting: Append a MASTER PORTFOLIO row at the bottom of the output DataFrame.

Phase 2: Corporate Action "Ancestry" \& Redemption Logic

Problem: Corporate spin-offs (e.g., Kinnevik distributing Zalando or Tele2) and redemptions (Kinnevik IL B) are currently processed as standard sales or independent transfers, artificially depressing the parent ticker’s historical ROI.

Requirements:

New Lexicon Mapping: Add REDEMPTION to TRANSACTION\_TYPE\_MAPPING in config.py.

Ledger Mechanics (ledger.py): Process REDEMPTION events by deducting units while re-allocating realized gains directly back to the parent asset's profit pool.

Ancestry Matrix (config.py): Define an ANCESTRY\_MAP dictionary (e.g., {'Kinnevik B': \['Zalando', 'Tele2']}).

Parent-Child Aggregation (portfolio\_metrics.py): Add an "Adjusted Total Return" metric that combines child spin-off gains into the parent stock's lifetime performance.

Phase 3: Portfolio Exposure Metadata (Risk Analytics)

Problem: The system lacks risk breakdown by Sector, Geography, and Market Cap.

Requirements:

YFinance Metadata Extraction (portfolio\_metrics.py): Query yf.Ticker().info during batch price retrieval to extract sector, country, and marketCap.

Market Cap Categorizer: Implement a helper function to convert raw market caps into standard buckets (Mega, Large, Mid, Small, Micro) normalized to SEK.

Mutual Fund Exposure Overrides (config.py): Create an EXPOSURE\_OVERRIDES dictionary for unlisted funds (e.g., Avanza Småbolag) to supply hardcoded sector/country tags.

Visualization Additions: Build a Geographic Heatmap (px.choropleth) and a Country > Sector > Ticker Sunburst chart.

Phase 4: Live Updates \& Real-Time Sync (Two-Step Implementation)

Step 1: Hybrid Google Sheets Live Refresh (Easiest / Immediate)

Stocks \& ETFs: Maintain native =GOOGLEFINANCE() formulas in ledger.py for continuous, zero-cost 15-minute price updates directly inside Google Sheets.

Mutual Funds \& Unlisted Assets: Mutual funds calculate NAVs once per day. Implement one of two triggers:

Option A (Google Apps Script): Attach a custom script to a button inside Google Sheets ("🔄 Refresh Mutual Funds") that pings Avanza’s public endpoint (/api/fund-guide/guide/{fund\_id}) and updates NAV cells directly.

Option B (gspread Python Sync): Use gspread in scraper.py to push scraped NAVs from ticker\_mapping.json directly into the live Google Sheet on demand.

Step 2: Full Streamlit Web GUI Engine (Subsequent Patch)

Web Dashboard: Wrap main.py in a Streamlit web application (app.py).

Intelligent Price Caching:

Cache stock/ETF prices for 5 minutes using @st.cache\_data(ttl=300).

Cache mutual fund NAVs for 12 hours using @st.cache\_data(ttl=43200).

GUI Features:

One-Click Refresh Button: A prominent UI button to clear cache and re-trigger pipeline execution.

Interactive Data Grids: Filterable, searchable tables for live holdings and historical transactions.

Embedded Plotly Charts: Render all Plotly HTML dashboards (Viz\_1 through Viz\_5) directly inside tabbed views.

Drag-and-Drop Ingestion: Direct file-uploader widget to drop raw broker CSVs into data/raw/.

Phase 5: Advanced Quant Modules (Optional Add-Ons)

Automated Rebalancing Engine: Compare current asset weights (portfolio\_metrics.py) against target allocation arrays in config.py to generate exact trade orders.

Forward Dividend Projection: Extract dividendYield via yfinance to project expected 12-month forward dividend cash flow.

Institutional Risk Analytics: Compute Max Drawdown and Sharpe Ratio directly from Historical\_Performance.csv against the S\&P 500 benchmark.

Swedish ISK Tax Drag Simulator: Model capital growth in an ISK (flat annual tax) versus a standard AF account (30% capital gains tax) based on historical portfolio turnover.

