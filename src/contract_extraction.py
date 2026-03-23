from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
from dateutil.relativedelta import relativedelta
from pypdf import PdfReader

from .config import CONTRACTS_DIR, EXTRACTED_CONTRACTS_PATH, RAW_CONTRACT_TEXT_PATH


MONTH_NAME_TO_NUMBER = {
    "janeiro": 1,
    "fevereiro": 2,
    "março": 3,
    "marco": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}


@dataclass
class ExtractedRule:
    contract_id: str
    supplier_name: str
    contract_title: str
    start_date: str
    end_date: str
    expected_amount: float
    schedule_type: str
    due_day: int | None
    business_day_n: int | None
    due_months: str
    acceptance_date: str
    days_after_acceptance: int | None
    extraction_status: str
    extraction_notes: str


def _extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def build_raw_contract_dataset(contracts_dir: Path | None = None) -> pd.DataFrame:
    contracts_dir = contracts_dir or CONTRACTS_DIR
    rows = []
    for pdf_path in sorted(contracts_dir.glob("*.pdf")):
        text = _extract_text(pdf_path)
        rows.append({"contract_id": pdf_path.stem, "file_name": pdf_path.name, "text": text})

    df = pd.DataFrame(rows)
    RAW_CONTRACT_TEXT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_CONTRACT_TEXT_PATH, index=False)
    return df


def _search(pattern: str, text: str) -> re.Match[str] | None:
    return re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)


def _extract_rule(contract_id: str, text: str) -> ExtractedRule:
    supplier = _search(r"(?:CONTRATADA|Contratada|Fornecedor):\s*(.+?)(?=\s+(?:OBJETO|Objeto|In[ií]cio do projeto|Per[ií]odo contratual|Prazo|VIGÊNCIA))", text)
    if supplier is None:
        supplier = _search(r"PARTES:\s*Banco\s+XYZ\s+e\s+(.+?)(?=\s+(?:OBJETO|Objeto|VIGÊNCIA))", text)
    title = _search(r"(?:OBJETO|Objeto):\s*(.+?)(?=\s+(?:VIGÊNCIA|VIGÊNCIA CONTRATUAL|Per[ií]odo contratual|Prazo|In[ií]cio do projeto|Cl[áa]usula|Da forma de pagamento|Condição de pagamento|CLÁUSULA))", text)
    vigencia = _search(r"(?:VIGÊNCIA|VIGÊNCIA CONTRATUAL|Período contratual|Prazo):\s*(?:de\s*)?(\d{2}/\d{2}/\d{4}).*?(\d{2}/\d{2}/\d{4})", text)
    project_start = _search(r"In[ií]cio do projeto:\s*(\d{2}/\d{2}/\d{4})", text)
    monthly_fixed = _search(r"dia\s+(\d{1,2})\s+de\s+cada\s+m[eê]s", text)
    business_day = _search(r"(\d{1,2})[ºo]?\s+dia\s+[úu]til", text)
    quarterly = _search(r"trimestral.*?dia\s+(\d{1,2}).*?(março|marco).*?(junho).*?(setembro).*?(dezembro)", text)
    one_time = _search(r"parcela\s+[úu]nica.*?(\d+)\s*\((?:trinta|[a-zçã]+)\)\s+dias.*?aceite.*?(\d{2}/\d{2}/\d{4})", text)
    amount_match = _search(r"R\$\s*([\d\.]+,\d{2})", text)

    supplier_name = re.sub(r"\s+", " ", supplier.group(1)).strip().rstrip(".") if supplier else ""
    contract_title = re.sub(r"\s+", " ", title.group(1)).strip().rstrip(".") if title else ""
    contract_title = contract_title.split("Início do projeto")[0].strip().rstrip(".")
    start_date = pd.to_datetime(vigencia.group(1), dayfirst=True).date().isoformat() if vigencia else (
        pd.to_datetime(project_start.group(1), dayfirst=True).date().isoformat() if project_start else ""
    )
    end_date = pd.to_datetime(vigencia.group(2), dayfirst=True).date().isoformat() if vigencia else ""
    expected_amount = float(amount_match.group(1).replace(".", "").replace(",", ".")) if amount_match else 0.0

    if business_day:
        return ExtractedRule(
            contract_id=contract_id,
            supplier_name=supplier_name,
            contract_title=contract_title,
            start_date=start_date,
            end_date=end_date,
            expected_amount=expected_amount,
            schedule_type="monthly_business_day",
            due_day=None,
            business_day_n=int(business_day.group(1)),
            due_months="",
            acceptance_date="",
            days_after_acceptance=None,
            extraction_status="ok",
            extraction_notes="Detected nth business day clause.",
        )

    if quarterly:
        return ExtractedRule(
            contract_id=contract_id,
            supplier_name=supplier_name,
            contract_title=contract_title,
            start_date=start_date,
            end_date=end_date,
            expected_amount=expected_amount,
            schedule_type="quarterly_fixed_day",
            due_day=int(quarterly.group(1)),
            business_day_n=None,
            due_months="3,6,9,12",
            acceptance_date="",
            days_after_acceptance=None,
            extraction_status="ok",
            extraction_notes="Detected quarterly schedule clause.",
        )

    if one_time:
        return ExtractedRule(
            contract_id=contract_id,
            supplier_name=supplier_name,
            contract_title=contract_title,
            start_date=start_date,
            end_date=end_date,
            expected_amount=expected_amount,
            schedule_type="one_time_after_acceptance",
            due_day=None,
            business_day_n=None,
            due_months="",
            acceptance_date=pd.to_datetime(one_time.group(2), dayfirst=True).date().isoformat(),
            days_after_acceptance=int(one_time.group(1)),
            extraction_status="ok",
            extraction_notes="Detected single payment after acceptance clause.",
        )

    if monthly_fixed:
        return ExtractedRule(
            contract_id=contract_id,
            supplier_name=supplier_name,
            contract_title=contract_title,
            start_date=start_date,
            end_date=end_date,
            expected_amount=expected_amount,
            schedule_type="monthly_fixed_day",
            due_day=int(monthly_fixed.group(1)),
            business_day_n=None,
            due_months="",
            acceptance_date="",
            days_after_acceptance=None,
            extraction_status="ok",
            extraction_notes="Detected fixed monthly due day clause.",
        )

    return ExtractedRule(
        contract_id=contract_id,
        supplier_name=supplier_name,
        contract_title=contract_title,
        start_date=start_date,
        end_date=end_date,
        expected_amount=expected_amount,
        schedule_type="unknown",
        due_day=None,
        business_day_n=None,
        due_months="",
        acceptance_date="",
        days_after_acceptance=None,
        extraction_status="needs_review",
        extraction_notes="Payment clause not matched by extraction rules.",
    )


def extract_contract_rules(raw_df: pd.DataFrame) -> pd.DataFrame:
    rows = [_extract_rule(row["contract_id"], row["text"]) for _, row in raw_df.iterrows()]
    extracted = pd.DataFrame(asdict(row) for row in rows)
    EXTRACTED_CONTRACTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    extracted.to_csv(EXTRACTED_CONTRACTS_PATH, index=False)
    return extracted
