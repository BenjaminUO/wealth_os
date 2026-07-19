"""
WEALTH OS - MASTER CONFIGURATION
This file serves as the absolute source of truth for all file paths, 
broker ingestion schemas, translation dictionaries, and market data overrides.
"""

from pathlib import Path

# ==========================================
# 1. DIRECTORY & FILE PATH ARCHITECTURE
# ==========================================
# Automatically resolves the absolute path to the root 'wealth_os' folder
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist upon initialization (prevents FileNotFoundError crashes)
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Centralized output files
TRANSACTIONS_FILE = PROCESSED_DIR / "combined_transactions.csv"
MAPPING_FILE = PROCESSED_DIR / "ticker_mapping.json"
PORTFOLIO_FILE = PROCESSED_DIR / "Google_Sheets_Live_Portfolio.csv"
VERIFIED_FILE = PROCESSED_DIR / "Google_Sheets_Live_Portfolio_Verified.csv"
DUPLICATES_FILE = PROCESSED_DIR / "Flagged_Duplicates.csv"
METRICS_OUTPUT_FILE = PROCESSED_DIR / "Live_Metrics_Portfolio.csv"
HISTORICAL_PERFORMANCE_FILE = PROCESSED_DIR / "Historical_Performance.csv"


# ==========================================
# 2. BROKER INGESTION SCHEMAS
# ==========================================
# Defines exactly how to read and map raw exports from different Swedish banks
BROKER_PROFILES = {
    "Montrose": {
        "sep": ",",
        "encoding": "utf-8",
        "cols": {'Datum': 'Date', 'Typ': 'Type', 'Värdepapper / Beskr.': 'Asset',
                 'ISIN': 'ISIN', 'Antal': 'Quantity', 'Kurs': 'Price', 
                 'Totalt': 'Amount_SEK', 'Courtage': 'Fee', 'Konto': 'Account'}
    },
    "Nordnet": {
        "sep": "\t",
        "encoding": "utf-16", 
        "cols": {'Bokföringsdag': 'Date', 'Transaktionstyp': 'Type', 'Värdepapper': 'Asset',
                 'ISIN': 'ISIN', 'Antal': 'Quantity', 'Kurs': 'Price', 
                 'Belopp': 'Amount_SEK', 'Total Avgift': 'Fee', 'Depå': 'Account'}
    },
    "Avanza": {
        "sep": ";",
        "encoding": "utf-8",
        "cols": {'Datum': 'Date', 'Typ av transaktion': 'Type', 'Värdepapper/beskrivning': 'Asset',
                 'ISIN': 'ISIN', 'Antal': 'Quantity', 'Kurs': 'Price', 
                 'Belopp': 'Amount_SEK', 'Courtage': 'Fee', 'Konto': 'Account'}
    },
    "SAVR": {
        "sep": ";",
        "encoding": "utf-8",
        "cols": {'Datum': 'Date', 'Transaktionstyp': 'Type', 'Värdepapper/transaktionsnamn': 'Asset',
                 'ISIN': 'ISIN', 'Antal': 'Quantity', 'Kurs inkl. avgifter (kr)': 'Price', 
                 'Belopp (kr)': 'Amount_SEK', 'Konto': 'Account'}
    }
}


# ==========================================
# 3. THE MASTER TRANSACTION LEXICON
# ==========================================
# Translates 40+ chaotic Swedish banking terms into 13 strict Double-Entry Physics categories
TRANSACTION_TYPE_MAPPING = {
    # Buy / Sell
    'KÖP': 'BUY', 'KÖPT': 'BUY', 'TECKNING': 'BUY', 'TECKNING LIKVID': 'BUY',
    'SÄLJ': 'SELL', 'SÅLD': 'SELL', 'SÅLT': 'SELL', 'INLÖSEN': 'SELL', 
    'INLÖSENAKTIE': 'SELL', 'ÅTERKÖP': 'SELL', 'INLÖSEN LIKVID': 'SELL', 
    'DECIMALER LIKVID': 'SELL', 'BOKNING FRAKTIONSLIKVIDER': 'SELL',
    
    # Dividends & Interest
    'UTDELNING': 'DIVIDEND', 'AKTIELÅNEPROGRAMMET': 'DIVIDEND', 'UTBETALNING AKTIELÅN': 'DIVIDEND',
    'RÄNTA': 'INTEREST', 'INLÅNINGSRÄNTA': 'INTEREST', 'KAP RÄNTA': 'INTEREST',
    
    # Taxes & Fees
    'UTLÄNDSK KÄLLSKATT': 'TAX', 'SKATT': 'TAX', 'PRELIMINÄR KAPITALSKATT': 'TAX', 
    'AVKASTNINGSSKATT': 'TAX', 'AVKASTNINGSSKATT.': 'TAX', 'UTLÄNDSK SKATT': 'TAX', 
    'PRELIMINÄRSKATT': 'TAX', 'PRELSKATT UTD': 'TAX', 'PRELIMINÄRSKATT KAPITALRÄNTA': 'TAX', 'MOMS': 'TAX',
    'ÅTERBETALNING UTLÄNDSK KÄLLSKATT': 'TAX_REFUND', 'ÅTERBETALD KÄLLSKATT': 'TAX_REFUND',
    'AVGIFT': 'FEE', 'SAVRS FONDAVGIFT': 'FEE', 'ADR-AVGIFT': 'FEE', 'SMS-AVGIFT': 'FEE', 
    'RISKKOSTNAD': 'FEE', 'UTTAG AV RISKKOSTNAD': 'FEE', 'UTLÅNINGSRÄNTA': 'FEE', 
    'KAP. DEB RÄNTA': 'FEE', 'KAP ÖVERBEL.RÄNTA': 'FEE',
    
    # Cash Flow (Deposits / Withdrawals)
    'INSÄTTNING': 'DEPOSIT', 'DIREKTINSÄTTNING VIA SWISH': 'DEPOSIT', 'AUTOGIROINSÄTTNING': 'DEPOSIT', 
    'REALTIDSINSÄTTNING': 'DEPOSIT', 'PREMIEINBETALNING': 'DEPOSIT', 'INTERN ÖVERFÖRING': 'DEPOSIT', 
    'FLYTT FRÅN ANNAN BANK': 'DEPOSIT', 'ÖVERFÖRING': 'DEPOSIT', 'ÖVERFÖRING UNDERKONTO': 'DEPOSIT', 
    'ÖVERFÖRING FRÅN DELÅTERKÖP': 'DEPOSIT', 'ERSÄTTNING': 'DEPOSIT',
    'UTTAG': 'WITHDRAWAL', 'ÖVRIGT': 'WITHDRAWAL', 'UTBETALNING': 'WITHDRAWAL', 'BETALNING': 'WITHDRAWAL', 
    'DELÅTERKÖP AVA INTERNT': 'WITHDRAWAL', 'DDL DELÅTERKÖP VIA DATACLEARINGEN': 'WITHDRAWAL',
    
    # Spinoffs (Forces units to dilute safely without adding fake cost basis)
    'UTDELNING VÄRDEPAPPER': 'SPINOFF', 'UTDELNING INLÄGG VP': 'SPINOFF',
    
    # Share Transfers (Strictly for units, NOT cash)
    'VÄRDEPAPPERSINSÄTTNING': 'TRANSFER_IN', 'VP-ÖVERFÖRING IN': 'TRANSFER_IN', 'INLÄGG VP': 'TRANSFER_IN', 
    'EM INLÄGG VP': 'TRANSFER_IN', 'TILLDELNING INLÄGG': 'TRANSFER_IN', 'TECKNING INLÄGG': 'TRANSFER_IN',
    'VÄRDEPAPPERSUTTAG': 'TRANSFER_OUT', 'VP-ÖVERFÖRING UT': 'TRANSFER_OUT', 'UTBOKNING': 'TRANSFER_OUT', 
    'AVSKILJNING': 'TRANSFER_OUT', 'UTTAG VP': 'TRANSFER_OUT', 'EM UTTAG VP': 'TRANSFER_OUT', 
    'INLÖSEN UTTAG VP': 'TRANSFER_OUT', 'RENSNING UTTAG VP': 'TRANSFER_OUT', 'UTBOKNING FRAKTIONER': 'TRANSFER_OUT', 
    'DECIMALER UTTAG VP': 'TRANSFER_OUT', 'TECKNING RÄTTER': 'TRANSFER_OUT',
    
    # Corporate Actions
    'SPLIT': 'SPLIT', 'SPLIT INLÄGG VP': 'SPLIT', 'SPLIT UTTAG VP': 'SPLIT', 'SPLIT VÄRDEPAPPER': 'SPLIT', 
    'SPLIT NYTT VÄRDEPAPPER': 'SPLIT', 'BYTE INLÄGG VP': 'SPLIT', 'BYTE UTTAG VP': 'SPLIT', 
    'BYTE': 'SPLIT', 'TILLDELNING NYEMISSION': 'SPLIT',

    # Under the "Share Transfers" block (TRANSFER_IN):
    'TILLDELNING': 'TRANSFER_IN',          # Natively handles SAVR's BTA addition
    'TECKNING INLÄGG VP': 'TRANSFER_IN',   # Natively handles Nordnet's BTA addition

    # Under the "Share Transfers" block (TRANSFER_OUT):
    'TECKNING UT RÄTTER': 'TRANSFER_OUT',  # Natively handles Nordnet's TR removal
    'BYTE UTTAG VP': 'SPLIT',              # Matches Nordnet's BTA extraction
    'BYTE INLÄGG VP': 'SPLIT',              # Matches Nordnet's Share insertion
}

# Used to sweep all cash components into a single ledger asset
CASH_TYPES = ['DEPOSIT', 'WITHDRAWAL', 'INTEREST']


# ==========================================
# 4. ASSET STANDARDIZATION & OVERRIDES
# ==========================================
# Maps ISINs to a unified name to prevent duplicate ledgers from broker re-brandings
MANUAL_NAME_OVERRIDES = {
    'SE0007048020': 'Norion Bank',           
    'SE0000567729': 'Sensys Gatso Group',
    'SE0000412371': 'MTG B',
    'SE0014453221': 'Avanza Tech Solutions by Barrett',
    'SE0016844831': 'Volvo Car B',           
    'SE0012673267': 'Evolution',             
    'SE0015988019': 'Storskogen Group B',    
    'SE0015811963': 'SBB Norden B',          
    'US01609W1027': 'Alibaba Group ADR',
    'US02079K1079': 'Alphabet Inc Class A',  
    'US30212W1009': 'eXp World',             
    'FI4000330972': 'Nanoform Finland',
    'US38268T1034': 'Gores Holdings VI',     
    'US17143M1053': 'Churchill Capital IV'   
}

# Maps string artifacts to clean names (The "Verisure/Robinhood/Prosus" Fix)
ASSET_RENAME_RULES = {
    'Volvo Car AB (publ)': 'Volvo Car B',
    'Shift Technologies, Inc.': 'Shift Technologies Inc',
    'Polestar ADR': 'Polestar Automotive Holding UK PLC',
    'GORES GUGGENHEIM INC': 'Polestar Automotive Holding UK PLC',
    'Collector AB': 'Norion Bank',
    'Oersted A/S': 'Ørsted',
    
    # --- ADD THESE NEW RULES ---
    'Alphabet A': 'Alphabet Inc Class A',
    'AVANT BRANDS INC': 'Avant Brands',
    'Storskogen B': 'Storskogen Group B',
    
    # --- THE VERISURE IPO FIX ---
    'ANSÖKAN VERISURE PLC': 'Verisure',
    'Ansökan Verisure PLC': 'Verisure',
    'VERISURE PLC': 'Verisure',
    
    # --- THE ROBINHOOD FIX ---
    'Robinhood Markets A': 'Robinhood',
    'Robinhood Markets Inc.': 'Robinhood',
    'Robinhood Markets, Inc. - Class A': 'Robinhood',
    
    # --- THE PROSUS FIX ---
    'Prosus N.V.': 'Prosus',
    'PROSUS N.V.': 'Prosus',

    # --- THE INTRUM FIX ---
    'INTRUM AB BTA': 'Intrum',
    'INTRUM JUSTITIA BTA': 'Intrum',
    'INTRUM': 'Intrum',
    'ELECTROLUX BTA A': 'Electrolux A',
    'ELECTROLUX BTA B': 'Electrolux B',
    'ELUX BTA A': 'Electrolux A',
    'ELUX BTA B': 'Electrolux B'
}


# ==========================================
# 5. MARKET DATA TICKER MAPPINGS
# ==========================================
# Forces specific assets to bypass the Yahoo Search API for 100% accuracy
MANUAL_TICKER_OVERRIDES = {
    # US Ticker Overrides
    "ALPHABET INC CLASS A": "NASDAQ:GOOGL",
    "ALPHABET A": "NASDAQ:GOOGL",
    "KLARNA GROUP": "NYSE:KLAR", 
    "CARNIVAL": "NYSE:CCL",
    "FOOT LOCKER": "NYSE:FL",
    "NORDSTROM": "NYSE:JWN",
    "WALGREENS BOOTS ALLIANCE INC": "NASDAQ:WBA",
    "MATTERPORT INC": "NASDAQ:MTTR",
    "VERVE GROUP MEDIA": "STO:VER",
    "EXP WORLD": "NASDAQ:AGNT",
    "ROBINHOOD": "NASDAQ:HOOD",           # <-- FIXED: Added NASDAQ prefix for safety
    "ROBINHOOD MARKETS A": "NASDAQ:HOOD", # <-- FIXED: Added NASDAQ prefix
    
    # Nordic Native Exchange Fixes
    "STORSKOGEN GROUP B": "STO:STOR-B",   # <-- FIXED: Put Storskogen back!
    "ZAPTEC": "FRA:6I4",
    "SCATEC": "FRA:66T",
    "SCANDINAVIAN ASTOR GROUP": "FRA:Y73",
    "SENSYS GATSO GROUP": "STO:SENS",
    "VETERANPOOLEN B": "FRA:QI5",
    "EMBEDDEDART GROUP": "STO:EAG",
    "NANOFORM FINLAND": "HEL:NANOF",
    "MILLICOM INT CELLULAR S.A. SDB": "STO:TIGO",
    
    # Standard Swedish Equities
    "OCTAVE INTELLIGENCE SDB": "NYSE:OSG",
    "COLLECTOR AB": "STO:NORION",
    "NORION BANK": "STO:NORION",
    "ATLAS COPCO B": "STO:ATCO-B",
    "SAGAX B": "STO:SAGA-B",
    "TRATON SE": "STO:8TRA",
    "KAMBI GROUP": "STO:KAMBI",
    "INVESTOR B": "STO:INVE-B",
    "QUICKBIT": "STO:QBIT",
    "ELECTROLUX A": "STO:ELUX-A",
    "ELECTROLUX B": "STO:ELUX-B",

    # Foreign/Global Overrides
    "EDP RENEWABLES, SA": "ELI:EDPR",        
    "CIELO WASTE SOLUTIONS": "CVE:CMC",      
    "PROSUS": "AMS:PRX",                     
    "ISHARES CORE S&P 500 UCITS ETF USD (ACC)": "AMS:CSPX",
    "XETRA-GOLD ETC": "FRA:4GLD",
    "AVANT BRANDS": "TSE:AVNT",
    "AVANT BRANDS INC": "TSE:AVNT",
    "EPIROC B": "STO:EPI-B",
    "VERISURE": "STO:VSURE",

    # Bankrupt / Acquired / Private (Bypass API entirely)
    "VALUNO GROUP": "N/A", "OX2 AB": "N/A", "NORDIC PAPER HOLDING AB": "N/A",
    "ORTHO CLINICAL DIAGNOSTICS HOLDINGS PLC": "N/A", 
    "SHIFT TECHNOLOGIES INC": "N/A", "TATTOOED CHEF INC": "N/A", 
    "GORES HOLDINGS VI INC": "N/A", "CHURCHILL CAPITAL IV CORP": "N/A",
    "MELTWATER ORD SHS": "N/A",

    # Corporate Action Artifacts (Bypass the API to save network time)
    "FRAKTIONSERSÄTTNING FÖRETAGSHÄNDELSER 2024": "N/A", "UTBETALNING AKTIELÅN": "N/A",
    "SKATTER/AVGIFTER KAPITALFÖRSÄKRING": "N/A", "LUXBRIGHT TR": "N/A", "LUXBRIGHT  TR": "N/A", 
    "LUXBRIGHT TR SELL": "N/A", "LUXBRIGHT AB TR": "N/A", "QUICKBIT TR": "N/A", "NIMBUS BOAT TR": "N/A",
    "MINESTO TR": "N/A", "READLY INTERNATIONAL TIA": "N/A", "FIRST VENTURE SWEDEN AB TR": "N/A", 
    "FIRST VENTURE SWEDEN TR B SELL": "N/A", "FASADGRUPPEN GROUP TR": "N/A", "NORDIC PAPER HOLDING TIA": "N/A",
    "LUXBRIGHT AB UR": "N/A", "LUXBRIGHT UR SELL": "N/A", "ELECTROLUX TR A": "N/A", "ELECTROLUX TR B": "N/A", 
    "INTRUM TR": "N/A", "KINNEVIK B INLÖSENAKTIE": "N/A", "BOLIDEN INLÖSENAKTIE 2021": "N/A",
    "BOLIDEN DR": "N/A", "KINNEVIK DR B": "N/A", "ANNEHEM FAST DR": "N/A", "ANSÖKAN NORDIC PAPER HOLDING (PUBL)": "N/A",
    "KINNEVIK INLÖSENAKTIE IL B 2021": "N/A", "KINNEVIK INLÖSENAKTIE IL B 2020": "N/A", "ANSÖKAN VERISURE PLC": "N/A",

    # Mutual Funds & ETFs (Handled by Direct NAV Scraper)
    "MS INVF US GROWTH A USD": "N/A", "HANETF FUTURE OF DEFENCE UCITS ETF - ACC": "N/A",
    "HANETF FUTURE OF EUROPEAN DEFENCE UCITS ETF": "N/A", "WISDOMTREE EUROPE DEFENCE UCITS ETF - EUR ACC": "N/A",
    "ISHARES GLOBAL CLEAN ENERGY TRANSITION UCITS ETF USD (DIST)": "N/A",
    "ROBECO SMART ENERGY D-EUR CAP": "N/A", "BNP CLEAN ENERGY SOLUTIONS C USD C": "N/A",
    "BGF NEXT GENERATION TECHNOLOGY A2": "N/A", "AVANZA ZERO": "N/A", "AVANZA GLOBAL": "N/A",
    "AVANZA SMÅBOLAG BY SKOGLUND": "N/A", "AMF AKTIEFOND SMÅBOLAG": "N/A",
    "SEB SVERIGEFOND SMÅBOLAG C/R": "N/A", "TIN NY TEKNIK A": "N/A",
    "SWEDBANK ROBUR NY TEKNIK A": "N/A", "PARETO SMÅBOLAGSFOND A": "N/A",

    "ROBINHOOD": "NASDAQ:HOOD",
    "STORSKOGEN GROUP B": "STO:STOR-B",

    "INTRUM AB TR": "N/A",
    "INTRUM JUSTITIA TR": "N/A",
    "INTRUM AB BTA": "N/A",
    "INTRUM JUSTITIA BTA": "N/A",
    "BOLAGSHÄNDELSE": "N/A",
    "INTRUM": "STO:INTRUM",
}

# Used to scrape internal backend APIs for unlisted mutual funds
DIRECT_FUND_IDS = {
    "AVANZA SMÅBOLAG BY SKOGLUND": "878733",
    "HANDELSBANKEN HÅLLBAR ENERGI (A1 SEK)": "325406",
    "PARETO SMÅBOLAGSFOND A": "367123"
}

# Used as a fast-path to bypass the search API for known assets
KNOWN_YAHOO_TICKERS = {
    "WÄSTBYGG": "WBGR-B.ST", "SBB NORDEN B": "SBB-B.ST", "ORRÖN ENERGY": "ORRON.ST",
    "REVOLUTIONRACE": "RVRC.ST", "FOOT LOCKER": "FL", "NORDSTROM": "JWN", 
    "WALGREENS BOOTS ALLIANCE": "WBA", "ØRSTED": "ORSTED.CO", "OERSTED A/S": "ORSTED.CO", 
    "MATTERPORT": "MTTR", "AMAZONCOM": "AMZN", "AMAZON.COM": "AMZN", 
    "FAST. BALDER B": "BALD-B.ST", "FAST BALDER B": "BALD-B.ST", "BALDER B": "BALD-B.ST", 
    "ROBINHOOD": "HOOD", "ROBINHOOD MARKETS A": "HOOD", "NORDNET": "SAVE.ST"
}


# ==========================================
# 6. GLOBAL FINANCIAL CONSTANTS
# ==========================================
# Maps Google Finance exchange prefixes to Yahoo Finance suffixes
EXCHANGE_SUFFIX_MAP = {
    "STO": ".ST", "CPH": ".CO", "HEL": ".HE", "OSL": ".OL",
    "FRA": ".DE", "LON": ".L",  "EPA": ".PA", "AMS": ".AS",
    "SWX": ".SW", "TSE": ".TO", "CVE": ".V",  "ELI": ".LS",
    "BME": ".MC", "BIT": ".MI", "VIE": ".VI", "ISE": ".IR", 
    "WSE": ".WA"
}

# The absolute fail-safes if the Yahoo FX API goes down during calculation
FALLBACK_FX_RATES = {
    "USD": 10.50, "EUR": 11.30, "GBP": 13.50, 
    "DKK": 1.50,  "NOK": 1.00,  "CAD": 7.70, "CHF": 11.80, "SEK": 1.00
}

# Core tickers required for the shadow portfolio backtester
CORE_MACRO_SYMBOLS = [
    "^GSPC", "SEK=X", "EURSEK=X", "GBPSEK=X", 
    "DKKSEK=X", "NOKSEK=X", "CADSEK=X", "CHFSEK=X"
]

MANUAL_CURRENCY_OVERRIDES = {
    "Verisure": "EUR"
}