from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pdf_generation import generate_contract_pdfs
from src.sample_payments import generate_sample_actual_payments


def main() -> None:
    pdfs = generate_contract_pdfs()
    payments = generate_sample_actual_payments()
    print(f"Generated PDFs: {len(pdfs)}")
    print(f"Generated payments: {len(payments)}")


if __name__ == "__main__":
    main()
