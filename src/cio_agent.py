"""
WEALTH OS - CHIEF INVESTMENT OFFICER (CIO) AGENT
Leverages the Google GenAI SDK with Google Search Grounding to perform 
high-level macroeconomic analysis, capital allocation audits, and strategic 
portfolio optimization based on real-time news and market sentiment.
"""

import os
import pandas as pd
from google import genai
from google.genai import types
from datetime import datetime
from pathlib import Path

# Import Master Configurations
from src.config import METRICS_OUTPUT_FILE, REPORTS_DIR

def generate_executive_briefing() -> str:
    """Synthesizes the raw metrics into a highly concentrated text payload."""
    if not METRICS_OUTPUT_FILE.exists():
        return "ERROR: Metrics file missing. Run portfolio_metrics.py first."

    df = pd.read_csv(METRICS_OUTPUT_FILE)
    
    cash_row = df[df['Name'] == 'SEK CASH']
    total_cash = float(cash_row['Units'].values[0]) if not cash_row.empty else 0.0
    
    active_equities = df[(df['Units'] > 0.001) & (df['Name'] != 'SEK CASH')].copy()
    
    if active_equities.empty:
        return "ERROR: The portfolio currently holds no active capital positions."

    total_invested = pd.to_numeric(active_equities['Total Invested Capital (SEK)'], errors='coerce').sum()
    total_system_value = pd.to_numeric(active_equities['Current Value (SEK)'], errors='coerce').sum() + total_cash
    cash_percentage = (total_cash / total_system_value * 100) if total_system_value > 0 else 0.0
    total_lifetime_profit = pd.to_numeric(active_equities['Total Profit (SEK)'], errors='coerce').sum()

    top_30 = active_equities.nlargest(30, 'Current Value (SEK)')
    top_30_list = "\n".join([
        f"- {r['Name']} (Ticker: {r['GF Ticker']}) | Market Value: {float(r['Current Value (SEK)']):,.0f} SEK ({r['Portfolio Weight (%)']}%) | "
        f"Invested: {float(r['Total Invested Capital (SEK)']):,.0f} SEK | Lifetime ROI: {r['Profitability (%)']}%"
        for _, r in top_30.iterrows()
    ])

    zombies = active_equities[(active_equities['Portfolio Weight (%)'] > 1.0) & (active_equities['Profitability (%)'] < 0.0)]
    zombie_list = "\n".join([
        f"- {r['Name']} | Dead Weight: {float(r['Current Value (SEK)']):,.0f} SEK ({r['Portfolio Weight (%)']}%) | "
        f"Loss: {float(r['Total Profit (SEK)']):,.0f} SEK ({r['Profitability (%)']}%)"
        for _, r in zombies.iterrows()
    ]) if not zombies.empty else "- No significant zombie assets detected."

    yielders = active_equities[active_equities['Yield on Cost (%)'] > 2.0].nlargest(5, 'Yield on Cost (%)')
    yield_list = "\n".join([
        f"- {r['Name']} | Yield on Cost: {r['Yield on Cost (%)']}% | Net Dividends Paid: {float(r['Net Dividends']):,.0f} SEK"
        for _, r in yielders.iterrows()
    ]) if not yielders.empty else "- No significant dividend yielders detected."

    briefing = f"""
    MACRO SYSTEM SUMMARY:
    - Total System Net Worth: {total_system_value:,.0f} SEK
    - Total Cash Reserve: {total_cash:,.0f} SEK ({cash_percentage:.1f}% of total)
    - Total Historical Invested Capital: {total_invested:,.0f} SEK
    - Total Lifetime Profit Generated: {total_lifetime_profit:,.0f} SEK
    - Total Active Equity Positions: {len(active_equities)}

    CLIENT INVESTMENT PHILOSOPHY:
    The client employs a highly diversified, incremental buying strategy ("putting in a little bit whenever I find something interesting"). They believe this breadth offers a strong diversification advantage ("hopefully a few will do well").

    LIQUIDITY & TAX CONTEXT:
    The client operates within the Swedish tax system. Capital is primarily held in an ISK (Investeringssparkonto) subject to an annual 'schablonskatt' (~1.08% drag on total value). However, a portion of the uninvested SEK Cash Reserve sits in interest-bearing savings accounts (räntekonto), which mitigates some of the inflation and tax drag.

    TOP 30 CORE HOLDINGS (Ranked by Current Market Value):
    {top_30_list}

    ZOMBIE ASSET RADAR (Negative Yield, >1% Weight):
    {zombie_list}

    YIELD & CASH COW RADAR (Top 5 by Yield on Cost):
    {yield_list}
    """
    return briefing

def run_portfolio_agent():
    print("\n🧠 Compiling financial intelligence and activating web-search for the Master Advisor...")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("🚨 CRITICAL ERROR: 'GEMINI_API_KEY' environment variable is missing.")
        return

    # Initialize the NEW SDK Client
    client = genai.Client(api_key=api_key)

    executive_briefing = generate_executive_briefing()
    if "ERROR" in executive_briefing:
        print(f"🚨 {executive_briefing}")
        return
        
    today = datetime.now().strftime("%Y-%m-%d")

    system_instruction = (
        "You are the Chief Investment Officer (CIO) of an elite Swedish Family Office. I am your client. "
        "You provide highly objective, data-driven portfolio audits. "
        "You must balance professional financial reality with empathy for the client's chosen strategy. "
        "You are equipped with Google Search capabilities. You MUST search the web for real-time news "
        "to inform your analysis, especially regarding the client's largest holdings."
    )

    prompt = f"""
    Today is {today}. Review my consolidated system data payload below and provide your strategic audit.

    {executive_briefing}

    YOUR MANDATE (Respond with hierarchical Markdown, crisp, professional, and actionable):
    
    1. THE MACRO & LIQUIDITY VERDICT: Evaluate my cash reserve ({executive_briefing.split('Total Cash Reserve: ')[1].split('SEK')[0].strip()} SEK). Acknowledge that some of this is in interest-bearing accounts, but analyze if my overall liquidity ratio is optimal for my net worth.
    
    2. THE DIVERSIFICATION DEBATE: Address my strategy of buying small amounts of many different stocks. Validate the psychological ease and diversification benefits of this approach, but candidly explain the mathematical realities (e.g., 'diworsification', the dilution of winners, and the portfolio tail risk). Strike a balance between respect and professional advice.
    
    3. LIVE MARKET INTELLIGENCE (Search Required): Use your Google Search capabilities to find recent news, earnings reports, or macroeconomic catalysts affecting my heaviest-weighted stocks and biggest movers. Highlight any critical red flags or massive tailwinds.
    
    4. YIELD STRATEGY & ISK DRAG: Analyze my dividend generators against the ~1.08% ISK 'schablonskatt'. Are my 'zombies' bleeding capital, or is my yield covering the system drag?
    
    5. SECTOR ROTATION & ACTION PLAN: Give me 3 specific, actionable maneuvers to execute next week based on your web search and data analysis.
    """

    try:
        print("   -> Transmitting briefing to Gemini and initiating Google Search Grounding...")
        
        # Enable Google Search Grounding Tool
        google_search_tool = types.Tool(google_search=types.GoogleSearch())
        
        # New SDK syntax for generating content
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3, # Slightly higher to allow for qualitative synthesis of news
                max_output_tokens=4000,
                system_instruction=system_instruction,
                tools=[google_search_tool] # Links the AI to the live internet
            )
        )
        
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = REPORTS_DIR / f"CIO_Master_Wealth_Report_{today}.md"
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# 🏛️ The Master Advisor Audit - {today}\n\n")
            f.write(response.text)
            
            # Append grounding metadata (citations) to the bottom of the report if available
            if response.candidates and response.candidates[0].grounding_metadata:
                f.write("\n\n---\n### 🔍 Search Sources & Citations\n")
                chunks = response.candidates[0].grounding_metadata.grounding_chunks
                for i, chunk in enumerate(chunks):
                    if hasattr(chunk, 'web') and chunk.web:
                        f.write(f"{i+1}. [{chunk.web.title}]({chunk.web.uri})\n")
            
        print("\n=========================================================")
        print(f"🏛️ THE MASTER ADVISOR HAS SPOKEN")
        print("=========================================================\n")
        
        # Print a preview of the action plan to the terminal
        action_plan_preview = response.text.split("THE CIO'S ACTION PLAN")[-1].strip()
        # Fallback if the AI uses a slightly different heading
        if not action_plan_preview or action_plan_preview == response.text.strip():
            action_plan_preview = response.text.split("ACTION PLAN")[-1].strip()
            
        if "5." in action_plan_preview:
            action_plan_preview = action_plan_preview.replace("5.", "", 1).strip()
        print(action_plan_preview)
        
        print(f"\n💾 Full strategic report (with live news citations) saved to: '{REPORTS_DIR.name}/{report_path.name}'")
        
    except Exception as e:
        print(f"🚨 API Execution Failure: {e}")

if __name__ == "__main__":
    run_portfolio_agent()