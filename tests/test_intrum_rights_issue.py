import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import src.cio_agent as cio_mod
from src.ledger import generate_portfolio
import src.ledger as ledger_mod


class IntrumRightsIssueTest(unittest.TestCase):
    def _build_intrum_frame(self):
        return pd.DataFrame([
            {
                'Date': '2026-06-29',
                'Bank': 'Avanza',
                'Asset': 'Intrum',
                'ISIN': 'SE0000936478',
                'Quantity': 100,
                'Price': 20.0,
                'Amount_SEK': -2000.0,
                'Fee': 0.0,
                'Original_Type': 'Köp',
                'Standard_Type': 'BUY',
            },
            {
                'Date': '2026-06-29',
                'Bank': 'Avanza',
                'Asset': 'Intrum',
                'ISIN': 'SE0000936478',
                'Quantity': 100,
                'Price': 2.45,
                'Amount_SEK': 0.0,
                'Fee': 0.0,
                'Original_Type': 'Teckning inlägg',
                'Standard_Type': 'TRANSFER_IN',
            },
        ])

    def test_intrum_rights_issue_uses_rights_price_as_gav(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            df = self._build_intrum_frame()

            ledger_mod.PORTFOLIO_FILE = tmp_path / 'portfolio.csv'
            ledger_mod.TRANSACTIONS_FILE = tmp_path / 'transactions.csv'
            ledger_mod.MAPPING_FILE = tmp_path / 'mapping.json'

            df.to_csv(ledger_mod.TRANSACTIONS_FILE, index=False)
            (tmp_path / 'mapping.json').write_text(
                '{"Intrum": {"ticker": "STO:INTRUM", "fallback_price": null, "fallback_currency": "SEK"}}',
                encoding='utf-8',
            )

            result = generate_portfolio(df)
            intrum_row = result.loc[result['Name'] == 'Intrum'].iloc[0]

            self.assertEqual(intrum_row['Average Buy Price'], 11.22)

    def test_portfolio_output_includes_current_value_column(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            df = self._build_intrum_frame()

            ledger_mod.PORTFOLIO_FILE = tmp_path / 'portfolio.csv'
            ledger_mod.TRANSACTIONS_FILE = tmp_path / 'transactions.csv'
            ledger_mod.MAPPING_FILE = tmp_path / 'mapping.json'

            df.to_csv(ledger_mod.TRANSACTIONS_FILE, index=False)
            (tmp_path / 'mapping.json').write_text(
                '{"Intrum": {"ticker": "STO:INTRUM", "fallback_price": null, "fallback_currency": "SEK"}}',
                encoding='utf-8',
            )

            result = generate_portfolio(df)
            self.assertIn('Current Value (SEK)', result.columns)
            intrum_row = result.loc[result['Name'] == 'Intrum'].iloc[0]
            self.assertTrue(str(intrum_row['Current Value (SEK)']).startswith('=C'))

    def test_special_manual_ticker_overrides_are_correct(self):
        from src.config import MANUAL_TICKER_OVERRIDES, ASSET_RENAME_RULES, MANUAL_CURRENCY_OVERRIDES

        self.assertEqual(MANUAL_TICKER_OVERRIDES.get('VERISURE'), 'STO:VSURE')
        self.assertEqual(MANUAL_TICKER_OVERRIDES.get('ZAPTEC'), 'FRA:6I4')
        self.assertEqual(MANUAL_TICKER_OVERRIDES.get('SCATEC'), 'FRA:66T')
        self.assertEqual(MANUAL_TICKER_OVERRIDES.get('AVANT BRANDS'), 'TSE:AVNT')
        self.assertEqual(MANUAL_TICKER_OVERRIDES.get('AVANT BRANDS INC'), 'TSE:AVNT')
        self.assertEqual(MANUAL_TICKER_OVERRIDES.get('VERVE GROUP MEDIA'), 'STO:VER')
        self.assertEqual(MANUAL_TICKER_OVERRIDES.get('EXP WORLD'), 'NASDAQ:AGNT')
        self.assertEqual(ASSET_RENAME_RULES.get('ELECTROLUX BTA A'), 'Electrolux A')
        self.assertEqual(ASSET_RENAME_RULES.get('ELECTROLUX BTA B'), 'Electrolux B')
        self.assertEqual(MANUAL_CURRENCY_OVERRIDES.get('Verisure'), 'EUR')

    def test_vsure_st_currency_override(self):
        from src.utils import google_to_yahoo, get_yf_currency

        self.assertEqual(google_to_yahoo('STO:VSURE'), 'VSURE.ST')
        self.assertEqual(get_yf_currency('VSURE.ST'), ('EUR', 1.0))

    def test_run_portfolio_agent_retries_before_stopping(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test-key'}, clear=False):
            with patch('src.cio_agent.generate_executive_briefing', return_value='briefing'), \
                 patch('src.cio_agent.genai.Client') as mock_client, \
                 patch('src.cio_agent.time.sleep', return_value=None) as mock_sleep:
                mock_response = type('Response', (), {'text': 'ok', 'candidates': []})()
                mock_client.return_value.models.generate_content.side_effect = RuntimeError('boom')

                cio_mod.run_portfolio_agent(max_retries=3, retry_wait_seconds=0)

                self.assertEqual(mock_client.return_value.models.generate_content.call_count, 3)
                self.assertEqual(mock_sleep.call_count, 2)


if __name__ == '__main__':
    unittest.main()
