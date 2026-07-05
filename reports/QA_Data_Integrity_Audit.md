# 🕵️ Master AI Data Integrity Audit Report

## ⚠️ TICKER MAPPING ANOMALIES
> **ACTION REQUIRED:** If the AI is correct, update `MANUAL_TICKER_OVERRIDES` in `src/config.py`.

### 🎯 Asset: Nordnet
- **Current Ticker:** ❌ `STO:SAVE`
- **Suggested Ticker:** ✅ `STO:NNOW`
- **AI Reasoning:** STO:SAVE is the ticker for Savosolar, not Nordnet. Nordnet's correct ticker is STO:NNOW.

### 🎯 Asset: Storskogen Group B
- **Current Ticker:** ❌ `STO:NIBE-B`
- **Suggested Ticker:** ✅ `STO:STOR-B`
- **AI Reasoning:** STO:NIBE-B is the ticker for NIBE Industrier B, not Storskogen Group B. Storskogen Group B's correct ticker is STO:STOR-B.

### 🎯 Asset: Asmodee
- **Current Ticker:** ❌ `STO:ASMDEE-B`
- **Suggested Ticker:** ✅ `Not Publicly Traded`
- **AI Reasoning:** Asmodee Group is not publicly traded under STO:ASMDEE-B. It was acquired by Embracer Group and is no longer an independently listed entity.

### 🎯 Asset: Klarna Group
- **Current Ticker:** ❌ `NYSE:KLAR`
- **Suggested Ticker:** ✅ `Not Publicly Traded`
- **AI Reasoning:** Klarna Group is a private company and is not publicly traded on NYSE:KLAR or any other exchange.

### 🎯 Asset: Coffee Stain Group B
- **Current Ticker:** ❌ `STO:COFFEE-B`
- **Suggested Ticker:** ✅ `Not Publicly Traded`
- **AI Reasoning:** Coffee Stain Group is a subsidiary of Embracer Group and is not independently publicly traded under STO:COFFEE-B.

### 🎯 Asset: Octave Intelligence SDB
- **Current Ticker:** ❌ `NYSE:OSG`
- **Suggested Ticker:** ✅ `STO:OCTAVE`
- **AI Reasoning:** NYSE:OSG is the ticker for Overseas Shipholding Group, not Octave Intelligence SDB. Octave Intelligence AB is listed on Nasdaq First North Growth Market with ticker STO:OCTAVE.

---

## ⚠️ TRANSACTION CATEGORIZATION ANOMALIES
> **ACTION REQUIRED:** If correct, update the `TRANSACTION_TYPE_MAPPING` dictionary in `src/config.py`.

### 📅 2020-08-26 | KINNEVIK DR B
- **Bank Raw Label:** `Utdelning värdepapper`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 4: 'Utdelning värdepapper' (Dividend paid in shares) MUST be mapped to TRANSFER_IN, not SPLIT.

### 📅 2020-08-26 | KINNEVIK DR B
- **Bank Raw Label:** `Utdelning värdepapper`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 4: 'Utdelning värdepapper' (Dividend paid in shares) MUST be mapped to TRANSFER_IN, not SPLIT.

### 📅 2020-09-22 | Park Lawn Corp
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Objectively illogical: 'Värdepappersinsättning' (securities deposit) should be mapped to TRANSFER_IN, not SPLIT.

### 📅 2020-09-22 | Veolia Environnement S.A.
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Objectively illogical: 'Värdepappersinsättning' (securities deposit) should be mapped to TRANSFER_IN, not SPLIT.

### 📅 2020-09-22 | Alphabet Inc Class A
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Objectively illogical: 'Värdepappersuttag' (securities withdrawal) should be mapped to TRANSFER_OUT, not SPLIT.

### 📅 2020-09-22 | Dropbox A
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Objectively illogical: 'Värdepappersuttag' (securities withdrawal) should be mapped to TRANSFER_OUT, not SPLIT.

### 📅 2020-09-22 | Alphabet Inc Class A
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Objectively illogical: 'Värdepappersinsättning' (securities deposit) should be mapped to TRANSFER_IN, not SPLIT.

### 📅 2020-09-22 | Dropbox A
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Objectively illogical: 'Värdepappersinsättning' (securities deposit) should be mapped to TRANSFER_IN, not SPLIT.

### 📅 2020-09-22 | Veolia Environnement S.A.
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-09-22 | MTG B
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-09-22 | MTG B
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-09-22 | MILLICOM INT CELLULAR S.A. SDB
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-09-22 | Valuno Group
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-09-22 | Sensys Gatso Group
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-09-22 | MILLICOM INT CELLULAR S.A. SDB
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-09-22 | Norion Bank
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-09-22 | Nanoform Finland
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-09-22 | Norion Bank
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-09-22 | Nanoform Finland
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-09-22 | READLY INTERNATIONAL AB
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-09-22 | Valuno Group
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-09-22 | Sensys Gatso Group
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-09-22 | READLY INTERNATIONAL AB
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-09-22 | Avanza Tech Solutions by Barrett
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-09-22 | BGF World Technology A2
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-09-22 | MS INVF Global Opportunity A
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-09-22 | Avanza Tech Solutions by Barrett
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-09-22 | MS INVF Global Opportunity A
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-09-22 | BGF World Technology A2
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-11-12 | Avanza Tech Solutions by Barrett
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-11-12 | Avanza Tech Solutions by Barrett
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-11-12 | BGF World Technology A2
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-11-12 | BGF World Technology A2
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-12-09 | ANNEHEM FAST DR
- **Bank Raw Label:** `Utdelning värdepapper`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 4 violated: 'Utdelning värdepapper' MUST be mapped to TRANSFER_IN.

### 📅 2020-12-09 | ANNEHEM FAST DR
- **Bank Raw Label:** `Utdelning värdepapper`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 4 violated: 'Utdelning värdepapper' MUST be mapped to TRANSFER_IN.

### 📅 2020-11-18 | Avanza Tech Solutions by Barrett
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-11-18 | Avanza Tech Solutions by Barrett
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-11-18 | Sensys Gatso Group
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-11-18 | MTG B
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-11-18 | Sensys Gatso Group
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-11-18 | MTG B
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-11-18 | READLY INTERNATIONAL AB
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-11-18 | Norion Bank
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-11-18 | READLY INTERNATIONAL AB
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-11-18 | Norion Bank
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-11-18 | Valuno Group
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-11-18 | Valuno Group
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-11-18 | Nanoform Finland
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-11-18 | MILLICOM INT CELLULAR S.A. SDB
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-11-18 | Nanoform Finland
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-11-18 | MILLICOM INT CELLULAR S.A. SDB
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-11-24 | Avanza Tech Solutions by Barrett
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-11-24 | Avanza Tech Solutions by Barrett
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-12-18 | Avanza Tech Solutions by Barrett
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2020-12-18 | Avanza Tech Solutions by Barrett
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-12-23 | Tattooed Chef Inc
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_OUT is for ASSET SHARES.

### 📅 2020-12-23 | Tattooed Chef Inc
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Illogical mapping for securities transfer. Rule 1 states TRANSFER_IN is for ASSET SHARES.

### 📅 2021-04-06 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6: 'Uttag' for 'SEK CASH' must be WITHDRAWAL, not FEE.

### 📅 2021-05-07 | BOLIDEN DR
- **Bank Raw Label:** `Utdelning v
depapper`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 4: 'Utdelning v
depapper' must be mapped to TRANSFER_IN.

### 📅 2021-05-07 | BOLIDEN DR
- **Bank Raw Label:** `Utdelning v
depapper`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 4: 'Utdelning v
depapper' must be mapped to TRANSFER_IN.

### 📅 2021-05-18 | KINNEVIK DR B
- **Bank Raw Label:** `Utdelning v
depapper`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 4: 'Utdelning v
depapper' must be mapped to TRANSFER_IN.

### 📅 2021-05-18 | KINNEVIK DR B
- **Bank Raw Label:** `Utdelning v
depapper`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 4: 'Utdelning v
depapper' must be mapped to TRANSFER_IN.

### 📅 2021-07-05 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6: 'Uttag' for 'SEK CASH' must be WITHDRAWAL, not FEE.

### 📅 2021-10-05 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 violated: 'Uttag' for cash (not 'SAVRS FONDAVGIFT') must be WITHDRAWAL.

### 📅 2022-01-05 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 violated: 'Uttag' for cash (not 'SAVRS FONDAVGIFT') must be WITHDRAWAL.

### 📅 2022-04-06 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 violated: 'Uttag' for cash (not 'SAVRS FONDAVGIFT') must be WITHDRAWAL.

### 📅 2022-07-13 | QuidelOrtho
- **Bank Raw Label:** `Utdelning värdepapper`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 4 violated: 'Utdelning värdepapper' must be mapped to TRANSFER_IN.

### 📅 2022-10-05 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 violation: 'Uttag' for SEK CASH (not 'SAVRS FONDAVGIFT') must be mapped to WITHDRAWAL.

### 📅 2023-02-20 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 violation: 'Uttag' for SEK CASH (not 'SAVRS FONDAVGIFT') must be mapped to WITHDRAWAL.

### 📅 2023-05-20 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 violation: 'Uttag' for SEK CASH (not 'SAVRS FONDAVGIFT') must be mapped to WITHDRAWAL.

### 📅 2023-08-20 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 violation: 'Uttag' for SEK CASH (not 'SAVRS FONDAVGIFT') must be mapped to WITHDRAWAL.

### 📅 2023-11-20 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 violation: 'Uttag' for SEK CASH (not 'SAVRS FONDAVGIFT') must be mapped to WITHDRAWAL.

### 📅 2024-07-29 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 violated: 'Uttag' for 'SEK CASH' (not 'SAVRS FONDAVGIFT') must be mapped to WITHDRAWAL, not FEE.

### 📅 2024-11-19 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 violated: 'Uttag' for 'SEK CASH' (not 'SAVRS FONDAVGIFT') must be mapped to WITHDRAWAL, not FEE.

### 📅 2025-01-14 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6: 'Uttag' for SEK CASH must be WITHDRAWAL, not FEE, unless the asset is 'SAVRS FONDAVGIFT'.

### 📅 2025-01-17 | SPDR S&P 500 UCITS ETF (Acc)
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Objectively illogical: 'Värdepappersinsättning' (Securities deposit) is a transfer of shares into the account, not a SPLIT. Should be TRANSFER_IN.

### 📅 2025-01-17 | Vanguard S&P 500 UCITS ETF - (USD) Acc
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Objectively illogical: 'Värdepappersinsättning' (Securities deposit) is a transfer of shares into the account, not a SPLIT. Should be TRANSFER_IN.

### 📅 2025-01-17 | iShares Core S&P 500 UCITS ETF USD (Acc)
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Objectively illogical: 'Värdepappersinsättning' (Securities deposit) is a transfer of shares into the account, not a SPLIT. Should be TRANSFER_IN.

### 📅 2025-01-17 | SPDR S&P 500 UCITS ETF (Acc)
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Objectively illogical: 'Värdepappersuttag' (Securities withdrawal) is a transfer of shares out of the account, not a SPLIT. Should be TRANSFER_OUT.

### 📅 2025-01-17 | Vanguard S&P 500 UCITS ETF - (USD) Acc
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Objectively illogical: 'Värdepappersuttag' (Securities withdrawal) is a transfer of shares out of the account, not a SPLIT. Should be TRANSFER_OUT.

### 📅 2025-01-17 | iShares Core S&P 500 UCITS ETF USD (Acc)
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Objectively illogical: 'Värdepappersuttag' (Securities withdrawal) is a transfer of shares out of the account, not a SPLIT. Should be TRANSFER_OUT.

### 📅 2025-01-31 | Avanza Zero
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Objectively illogical: 'Värdepappersinsättning' (Securities deposit) is a transfer of shares into the account, not a SPLIT. Should be TRANSFER_IN.

### 📅 2025-01-31 | Avanza Global
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Objectively illogical: 'Värdepappersinsättning' (Securities deposit) is a transfer of shares into the account, not a SPLIT. Should be TRANSFER_IN.

### 📅 2025-01-31 | Avanza Zero
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Objectively illogical: 'Värdepappersuttag' (Securities withdrawal) is a transfer of shares out of the account, not a SPLIT. Should be TRANSFER_OUT.

### 📅 2025-01-31 | Avanza Global
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Objectively illogical: 'Värdepappersuttag' (Securities withdrawal) is a transfer of shares out of the account, not a SPLIT. Should be TRANSFER_OUT.

### 📅 2025-02-26 | Avanza Zero
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 1: Värdepappersinsättning (securities deposit) is a share transfer in, not a split. TRANSFER_IN is strictly reserved for asset shares.

### 📅 2025-02-26 | Avanza Zero
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Rule 1: Värdepappersuttag (securities withdrawal) is a share transfer out, not a split. TRANSFER_OUT is strictly reserved for asset shares.

### 📅 2025-04-02 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6: Uttag (withdrawal) for SEK CASH should be mapped to WITHDRAWAL, not FEE, unless the asset is specifically 'SAVRS FONDAVGIFT'.

### 📅 2025-04-09 | Boliden
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (securities deposit) represents an inflow of asset shares and should be mapped to TRANSFER_IN, not SPLIT.

### 📅 2025-04-09 | Boliden
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (securities withdrawal) represents an outflow of asset shares and should be mapped to TRANSFER_OUT, not SPLIT.

### 📅 2025-06-17 | Luxbright AB TR
- **Bank Raw Label:** `INLÖSEN UTTAG VP`
- **Current Script Label:** ❌ `TRANSFER_OUT`
- **AI Suggested Label:** ✅ `SELL`
- **AI Reasoning:** Rule 3: 0 SEK Redemptions ("Inlösen") MUST be mapped to SELL, not SPLIT. TRANSFER_OUT is not the mandated type for this specific 'Inlösen' scenario.

### 📅 2025-07-02 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6: 'Uttag' is normally WITHDRAWAL, but if the asset is specifically 'SAVRS FONDAVGIFT', it MUST be mapped to FEE. Since the asset is 'SEK CASH' and not 'SAVRS FONDAVGIFT', it should be WITHDRAWAL.

### 📅 2025-08-29 | READLY INTERNATIONAL AB
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 1: 'Värdepappersinsättning' (securities deposit) is a movement of asset shares into the account. This should be mapped to TRANSFER_IN, as SPLIT is reserved for corporate actions that change the number of shares of an existing holding, not a direct deposit of shares.

### 📅 2025-08-29 | READLY INTERNATIONAL AB
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Rule 1: 'Värdepappersuttag' (securities withdrawal) is a movement of asset shares out of the account. This should be mapped to TRANSFER_OUT, as SPLIT is reserved for corporate actions that change the number of shares of an existing holding, not a direct withdrawal of shares.

### 📅 2025-09-30 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6: 'Uttag' for 'SEK CASH' is normally 'WITHDRAWAL', unless the asset is 'SAVRS FONDAVGIFT'.

### 📅 2025-12-23 | First Venture Sweden AB TR
- **Bank Raw Label:** `INLÖSEN UTTAG VP`
- **Current Script Label:** ❌ `TRANSFER_OUT`
- **AI Suggested Label:** ✅ `SELL`
- **AI Reasoning:** Rule 3 violated: 0 SEK Redemptions ("Inlösen") MUST be mapped to SELL, not SPLIT. Current type TRANSFER_OUT is incorrect.

### 📅 2026-01-19 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 violated: 'Uttag' for 'SEK CASH' must be mapped to WITHDRAWAL, not FEE, unless the asset is 'SAVRS FONDAVGIFT'.

### 📅 2026-03-02 | NORDIC PAPER HOLDING AB
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 1: TRANSFER_IN is strictly reserved for ASSET SHARES (Units). 'Värdepappersinsättning' is a deposit of shares.

### 📅 2026-03-02 | NORDIC PAPER HOLDING AB
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Rule 1: TRANSFER_OUT is strictly reserved for ASSET SHARES (Units). 'Värdepappersuttag' is a withdrawal of shares.

### 📅 2026-03-13 | FASADGRUPPEN GROUP TR
- **Bank Raw Label:** `Tilldelning nyemission`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 1: 'Tilldelning nyemission' (allotment new issue) represents an injection of shares and should be mapped to TRANSFER_IN.

### 📅 2026-03-16 | MTG B
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 1: TRANSFER_IN is strictly reserved for ASSET SHARES (Units). 'Värdepappersinsättning' is a deposit of shares.

### 📅 2026-03-16 | Lime Technologies
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | Asker Healthcare
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | Intrum
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | Kinnevik B
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | RaySearch Laboratories B
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | MEKO
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | MTG B
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | Lime Technologies
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | Asker Healthcare
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | Intrum
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | Kinnevik B
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | RaySearch Laboratories B
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-03-16 | MEKO
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-07 | SEK CASH
- **Bank Raw Label:** `Uttag`
- **Current Script Label:** ❌ `FEE`
- **AI Suggested Label:** ✅ `WITHDRAWAL`
- **AI Reasoning:** Rule 6 states 'Uttag' is normally WITHDRAWAL unless the asset is 'SAVRS FONDAVGIFT'. For 'SEK CASH', it should be WITHDRAWAL (also supported by Rule 2 for cash movements).

### 📅 2026-04-15 | EQT
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-15 | Munters Group AB
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-15 | Corem Property Group B
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-15 | Karnell
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-15 | Atlas Copco B
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-15 | Mips
- **Bank Raw Label:** `Värdepappersinsättning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Värdepappersinsättning (Securities deposit) implies an inflow of asset shares. Rule 1 states TRANSFER_IN is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-15 | EQT
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-15 | Munters Group AB
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-15 | Corem Property Group B
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-15 | Karnell
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-15 | Atlas Copco B
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-15 | Mips
- **Bank Raw Label:** `Värdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Värdepappersuttag (Securities withdrawal) implies an outflow of asset shares. Rule 1 states TRANSFER_OUT is for ASSET SHARES, not SPLIT, which is for internal adjustments.

### 📅 2026-04-29 | Intrum
- **Bank Raw Label:** `V

rdepappersins

ttning`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_IN`
- **AI Reasoning:** Rule 1 violated: 'Värdepappersinsättning' (securities deposit) is a movement of asset shares and must be mapped to TRANSFER_IN, not SPLIT.

### 📅 2026-04-29 | Intrum
- **Bank Raw Label:** `V

rdepappersuttag`
- **Current Script Label:** ❌ `SPLIT`
- **AI Suggested Label:** ✅ `TRANSFER_OUT`
- **AI Reasoning:** Rule 1 violated: 'Värdepappersuttag' (securities withdrawal) is a movement of asset shares and must be mapped to TRANSFER_OUT, not SPLIT.

### 📅 2026-05-06 | Luxbright AB UR
- **Bank Raw Label:** `INL

SEN UTTAG VP`
- **Current Script Label:** ❌ `TRANSFER_OUT`
- **AI Suggested Label:** ✅ `SELL`
- **AI Reasoning:** Rule 3 violated: 'INLÖSEN UTTAG VP' (0 SEK Redemption) must be mapped to SELL, not TRANSFER_OUT.

