"""
WEALTH OS - CHIEF INVESTMENT OFFICER (CIO) AGENT
Leverages the Google GenAI SDK with Google Search Grounding to perform 
high-level macroeconomic analysis, capital allocation audits, and strategic 
portfolio optimization based on real-time news and market sentiment.
"""

import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
load_dotenv(root_dir / ".env")

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
    The client operates within the Swedish tax system. Capital is primarily held in an ISK (Investeringssparkonto) subject to an annual 'schablonskatt' (~1.08% drag on total value). A about 50% portion of the uninvested SEK Cash Reserve sits in interest-bearing savings accounts (räntekonto) with about 2-2.5% interest.

    TOP 30 CORE HOLDINGS (Ranked by Current Market Value):
    {top_30_list}

    ZOMBIE ASSET RADAR (Negative Yield, >1% Weight):
    {zombie_list}

    YIELD & CASH COW RADAR (Top 5 by Yield on Cost):
    {yield_list}
    """
    return briefing

def _holding_rows(df: pd.DataFrame) -> list[str]:
    active_equities = df[(df['Units'] > 0.001) & (df['Name'] != 'SEK CASH')]
    top_holdings = active_equities.nlargest(30, 'Current Value (SEK)')
    return [
        f"- {row['Name']} | Ticker: {row['GF Ticker']} | Value: {float(row['Current Value (SEK)']):,.0f} SEK | "
        f"Weight: {row['Portfolio Weight (%)']}% | ROI: {row['Profitability (%)']}% | "
        f"Yield: {row['Yield on Cost (%)']}%"
        for _, row in top_holdings.iterrows()
    ]


def _grounding_sources(response) -> list[str]:
    sources = []
    for candidate in getattr(response, 'candidates', []) or []:
        metadata = getattr(candidate, 'grounding_metadata', None)
        for chunk in getattr(metadata, 'grounding_chunks', []) or []:
            web = getattr(chunk, 'web', None)
            if web and getattr(web, 'uri', None):
                source = f"[{getattr(web, 'title', web.uri)}]({web.uri})"
                if source not in sources:
                    sources.append(source)
    return sources


def _generate_response(
    client,
    prompt: str,
    system_instruction: str,
    max_output_tokens: int,
    max_retries: int,
    retry_wait_seconds: int,
    use_search: bool,
):
    tools = [types.Tool(google_search=types.GoogleSearch())] if use_search else None
    for attempt in range(1, max_retries + 1):
        try:
            config = types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=max_output_tokens,
                system_instruction=system_instruction,
            )
            if tools:
                config.tools = tools
            return client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=config,
            )
        except Exception as error:
            if attempt == max_retries:
                raise
            wait_seconds = retry_wait_seconds * (2 ** (attempt - 1))
            print(f"🚨 Attempt {attempt} failed: {error}")
            print(f"⏳ Retrying this step in {wait_seconds} seconds...")
            time.sleep(wait_seconds)


def run_portfolio_agent(max_retries: int = 3, retry_wait_seconds: int = 30):
    print("\n🧠 Running the CIO agent in four research passes and one synthesis pass...")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("🚨 CRITICAL ERROR: 'GEMINI_API_KEY' environment variable is missing.")
        return
    if not METRICS_OUTPUT_FILE.exists():
        print("🚨 Metrics file missing. Run portfolio_metrics.py first.")
        return

    client = genai.Client(api_key=api_key)
    today = datetime.now().strftime("%Y-%m-%d")
    metrics_df = pd.read_csv(METRICS_OUTPUT_FILE)
    holding_rows = _holding_rows(metrics_df)
    if not holding_rows:
        print("🚨 The portfolio currently holds no active capital positions.")
        return

    cash_row = metrics_df[metrics_df['Name'] == 'SEK CASH']
    total_cash = float(cash_row['Units'].iloc[0]) if not cash_row.empty else 0.0
    active_equities = metrics_df[(metrics_df['Units'] > 0.001) & (metrics_df['Name'] != 'SEK CASH')]
    total_value = pd.to_numeric(active_equities['Current Value (SEK)'], errors='coerce').sum() + total_cash
    cash_percentage = total_cash / total_value * 100 if total_value > 0 else 0.0

    research_instruction = (
        "You are a concise equity research analyst. Use Google Search to check recent developments "
        "from the last 30–90 days. Do not invent facts or prices. For every supplied holding, return "
        "exactly four short bullets: News/Catalyst, Bull Case, Key Risk, and Verdict (Accumulate, Hold, or Trim). "
        "Keep each holding under 100 words and cite important sources through grounded search."
    )
    holding_batches = [holding_rows[index:index + 8] for index in range(0, len(holding_rows), 8)]
    holding_batches = (holding_batches + [[]] * 4)[:4]
    research_results = []
    research_sources = []

    for batch_number, batch in enumerate(holding_batches, 1):
        if not batch:
            continue
        print(f"   -> Research pass {batch_number}/4 ({len(batch)} holdings)")
        batch_prompt = f"""
Today is {today}. Analyze only these holdings:
{chr(10).join(batch)}

Portfolio context: cash reserve {total_cash:,.0f} SEK ({cash_percentage:.1f}% of total system value).
Focus on material, recent information and keep the response compact.
"""
        try:
            response = _generate_response(
                client, batch_prompt, research_instruction, 1400,
                max_retries, retry_wait_seconds, use_search=True
            )
            text = response.text.strip()
            research_results.append(f"RESEARCH PASS {batch_number}\n{text}")
            research_sources.extend(_grounding_sources(response))
        except Exception as error:
            research_results.append(f"RESEARCH PASS {batch_number}\nUnavailable after retries: {error}")
            print(f"🚨 Research pass {batch_number} failed; continuing with the remaining passes.")

    research_digest = "\n\n".join(research_results)
    synthesis_instruction = (
        "You are the senior CIO for a private Swedish investor. Synthesize the supplied research into a "
        "concise, evidence-based report. Do not perform additional web searches. Clearly distinguish facts "
        "from judgment, avoid repeating every holding, and finish with a prioritized action plan."
    )
    synthesis_prompt = f"""
Today is {today}.

PORTFOLIO SNAPSHOT:
- Total system value: {total_value:,.0f} SEK
- Cash reserve: {total_cash:,.0f} SEK ({cash_percentage:.1f}%)
- Active positions analyzed: {len(holding_rows)}



Write the final report with these sections:
1. Executive Summary
2. Cash Position
3. Most Important Catalysts and Risks
4. Holding Verdicts, grouped into Accumulate, Hold, and Trim
5. THE CIO'S ACTION PLAN
Keep it under 2,500 words.
"""
    print("   -> Synthesis pass 5/5")
    try:
        final_response = _generate_response(
            client, synthesis_prompt, synthesis_instruction, 2600,
            max_retries, retry_wait_seconds, use_search=False
        )
    except Exception as error:
        print(f"🚨 Synthesis failed after retries: {error}")
        return

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    research_path = REPORTS_DIR / f"CIO_Research_Batches_{today}.md"
    report_path = REPORTS_DIR / f"CIO_Master_Wealth_Report_{today}.md"
    research_path.write_text(research_digest, encoding="utf-8")
    with report_path.open("w", encoding="utf-8") as report:
        report.write(f"# 🏛️ The Master Advisor Audit - {today}\n\n")
        report.write(final_response.text)
        all_sources = research_sources + _grounding_sources(final_response)
        if all_sources:
            report.write("\n\n---\n### 🔍 Search Sources & Citations\n")
            for index, source in enumerate(dict.fromkeys(all_sources), 1):
                report.write(f"{index}. {source}\n")

    print("\n=========================================================")
    print("🏛️ THE MASTER ADVISOR HAS SPOKEN")
    print("=========================================================\n")
    print(final_response.text)
    print(f"\n💾 Full strategic report saved to: '{REPORTS_DIR.name}/{report_path.name}'")
if __name__ == "__main__":
    run_portfolio_agent()