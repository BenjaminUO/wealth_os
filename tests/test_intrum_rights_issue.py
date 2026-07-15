import tempfile
import unittest
from pathlib import Path

import pandas as pd

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


if __name__ == '__main__':
    unittest.main()
