from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CONTRACTS_DIR = DATA_DIR / "contracts"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
PAYMENTS_INPUT_PATH = DATA_DIR / "payments_actual.csv"

RAW_CONTRACT_TEXT_PATH = BRONZE_DIR / "contract_texts.csv"
EXTRACTED_CONTRACTS_PATH = SILVER_DIR / "contract_payment_rules.csv"
PAYMENT_CALENDAR_PATH = GOLD_DIR / "payment_calendar.csv"
PAYMENT_MONITORING_PATH = GOLD_DIR / "payment_monitoring.csv"
AUDIT_CASES_PATH = GOLD_DIR / "audit_cases.csv"

