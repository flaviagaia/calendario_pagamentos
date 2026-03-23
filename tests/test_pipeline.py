from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.contract_extraction import build_raw_contract_dataset, extract_contract_rules
from src.pdf_generation import generate_contract_pdfs
from src.payment_calendar import build_payment_calendar
from src.sample_payments import generate_sample_actual_payments
from src.monitoring import evaluate_payment_calendar


class PaymentCalendarPipelineTest(unittest.TestCase):
    def test_end_to_end_pipeline_generates_audit_cases(self):
        generate_contract_pdfs()
        payments = generate_sample_actual_payments()
        raw = build_raw_contract_dataset()
        rules = extract_contract_rules(raw)
        calendar = build_payment_calendar(rules)
        monitoring, audit_cases = evaluate_payment_calendar(calendar, payments)

        self.assertEqual(len(raw), 5)
        self.assertTrue((rules["extraction_status"] == "ok").all())
        self.assertGreaterEqual(len(calendar), 10)
        self.assertGreaterEqual(len(monitoring), 10)
        self.assertGreaterEqual(len(audit_cases), 1)


if __name__ == "__main__":
    unittest.main()
