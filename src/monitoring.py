from __future__ import annotations

import pandas as pd

from .config import AUDIT_CASES_PATH, PAYMENT_MONITORING_PATH


def evaluate_payment_calendar(payment_calendar: pd.DataFrame, actual_payments: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    expected = payment_calendar.copy()
    expected["expected_payment_date"] = pd.to_datetime(expected["expected_payment_date"])
    expected = expected.sort_values(["contract_id", "expected_payment_date"]).reset_index(drop=True)
    cutoff_date = pd.to_datetime(actual_payments["actual_payment_date"]).max()
    expected = expected[expected["expected_payment_date"] <= cutoff_date].copy()
    expected["payment_occurrence"] = expected.groupby("contract_id").cumcount() + 1
    actual = actual_payments.copy()
    actual["actual_payment_date"] = pd.to_datetime(actual["actual_payment_date"])
    actual = actual.sort_values(["contract_id", "actual_payment_date"]).reset_index(drop=True)
    actual["payment_occurrence"] = actual.groupby("contract_id").cumcount() + 1

    merged = expected.merge(actual, on=["contract_id", "payment_occurrence"], how="left")
    merged["days_delta"] = (merged["actual_payment_date"] - merged["expected_payment_date"]).dt.days
    merged["amount_delta"] = merged["actual_amount"] - merged["expected_amount"]

    def classify(row: pd.Series) -> str:
        if pd.isna(row["actual_payment_date"]):
            return "missing_payment"
        if row["actual_payment_date"].date() == row["expected_payment_date"].date() and abs(row["amount_delta"]) < 0.01:
            return "on_time"
        if abs(row["amount_delta"]) >= 0.01:
            return "amount_mismatch"
        if row["days_delta"] < 0:
            return "paid_early"
        return "paid_late"

    merged["monitoring_status"] = merged.apply(classify, axis=1)
    merged["needs_attention"] = merged["monitoring_status"].isin(["missing_payment", "amount_mismatch", "paid_late"])
    merged["has_justification"] = merged["justification"].fillna("").str.strip().ne("")

    payment_monitoring = merged.sort_values(["contract_id", "expected_payment_date", "actual_payment_date"]).reset_index(drop=True)
    audit_cases = payment_monitoring[
        payment_monitoring["needs_attention"] & ~payment_monitoring["has_justification"]
    ].copy()
    audit_cases["audit_reason"] = audit_cases["monitoring_status"].map(
        {
            "missing_payment": "Expected payment not found in the execution log.",
            "amount_mismatch": "Actual amount differs from contracted amount and there is no justification.",
            "paid_late": "Payment happened after the contractual due date and there is no justification.",
        }
    )

    PAYMENT_MONITORING_PATH.parent.mkdir(parents=True, exist_ok=True)
    payment_monitoring.to_csv(PAYMENT_MONITORING_PATH, index=False)
    audit_cases.to_csv(AUDIT_CASES_PATH, index=False)
    return payment_monitoring, audit_cases
