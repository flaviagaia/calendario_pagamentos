from __future__ import annotations

import pandas as pd

from .config import PAYMENTS_INPUT_PATH


def generate_sample_actual_payments() -> pd.DataFrame:
    rows = [
        {"contract_id": "CTR-001", "actual_payment_date": "2026-01-10", "actual_amount": 14850.00, "justification": ""},
        {"contract_id": "CTR-001", "actual_payment_date": "2026-02-12", "actual_amount": 14850.00, "justification": "Atraso operacional no processamento bancário."},
        {"contract_id": "CTR-001", "actual_payment_date": "2026-03-18", "actual_amount": 14850.00, "justification": ""},
        {"contract_id": "CTR-002", "actual_payment_date": "2026-01-07", "actual_amount": 23500.00, "justification": ""},
        {"contract_id": "CTR-002", "actual_payment_date": "2026-02-06", "actual_amount": 23500.00, "justification": ""},
        {"contract_id": "CTR-003", "actual_payment_date": "2026-03-15", "actual_amount": 61500.00, "justification": ""},
        {"contract_id": "CTR-003", "actual_payment_date": "2026-06-18", "actual_amount": 61500.00, "justification": "Aguardando aceite de medição trimestral."},
        {"contract_id": "CTR-004", "actual_payment_date": "2026-04-30", "actual_amount": 98000.00, "justification": ""},
        {"contract_id": "CTR-005", "actual_payment_date": "2026-01-20", "actual_amount": 32100.00, "justification": ""},
        {"contract_id": "CTR-005", "actual_payment_date": "2026-02-24", "actual_amount": 32100.00, "justification": "Pagamento realizado após reprocessamento do arquivo de remessa."},
    ]
    df = pd.DataFrame(rows)
    PAYMENTS_INPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PAYMENTS_INPUT_PATH, index=False)
    return df
