from __future__ import annotations

import calendar
from datetime import date

import pandas as pd
from dateutil.relativedelta import relativedelta

from .config import PAYMENT_CALENDAR_PATH


def _safe_date(year: int, month: int, day: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day, last_day))


def _nth_business_day(year: int, month: int, n: int) -> date:
    business_days = pd.bdate_range(start=f"{year}-{month:02d}-01", end=f"{year}-{month:02d}-28") 
    # regenerate full month to avoid month length issues
    business_days = pd.bdate_range(start=f"{year}-{month:02d}-01", end=f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}")
    return business_days[n - 1].date()


def build_payment_calendar(contract_rules: pd.DataFrame) -> pd.DataFrame:
    calendar_rows: list[dict] = []

    for _, row in contract_rules.iterrows():
        start = pd.to_datetime(row["start_date"]).date() if row["start_date"] else None
        end = pd.to_datetime(row["end_date"]).date() if row["end_date"] else None
        if row["extraction_status"] != "ok":
            continue

        if row["schedule_type"] == "monthly_fixed_day" and start is not None and end is not None:
            cursor = start
            while cursor <= end:
                due_date = _safe_date(cursor.year, cursor.month, int(row["due_day"]))
                calendar_rows.append(
                    {
                        "contract_id": row["contract_id"],
                        "supplier_name": row["supplier_name"],
                        "competence_month": f"{cursor.year}-{cursor.month:02d}",
                        "expected_payment_date": due_date.isoformat(),
                        "expected_amount": row["expected_amount"],
                        "schedule_type": row["schedule_type"],
                    }
                )
                cursor = cursor + relativedelta(months=1)

        elif row["schedule_type"] == "monthly_business_day" and start is not None and end is not None:
            cursor = start
            while cursor <= end:
                due_date = _nth_business_day(cursor.year, cursor.month, int(row["business_day_n"]))
                calendar_rows.append(
                    {
                        "contract_id": row["contract_id"],
                        "supplier_name": row["supplier_name"],
                        "competence_month": f"{cursor.year}-{cursor.month:02d}",
                        "expected_payment_date": due_date.isoformat(),
                        "expected_amount": row["expected_amount"],
                        "schedule_type": row["schedule_type"],
                    }
                )
                cursor = cursor + relativedelta(months=1)

        elif row["schedule_type"] == "quarterly_fixed_day" and start is not None:
            months = [int(item) for item in str(row["due_months"]).split(",") if item]
            for month in months:
                due_date = _safe_date(start.year, month, int(row["due_day"]))
                calendar_rows.append(
                    {
                        "contract_id": row["contract_id"],
                        "supplier_name": row["supplier_name"],
                        "competence_month": f"{due_date.year}-{due_date.month:02d}",
                        "expected_payment_date": due_date.isoformat(),
                        "expected_amount": row["expected_amount"],
                        "schedule_type": row["schedule_type"],
                    }
                )

        elif row["schedule_type"] == "one_time_after_acceptance" and row["acceptance_date"]:
            acceptance_date = pd.to_datetime(row["acceptance_date"]).date()
            due_date = acceptance_date + relativedelta(days=int(row["days_after_acceptance"]))
            calendar_rows.append(
                {
                    "contract_id": row["contract_id"],
                    "supplier_name": row["supplier_name"],
                    "competence_month": due_date.strftime("%Y-%m"),
                    "expected_payment_date": due_date.isoformat(),
                    "expected_amount": row["expected_amount"],
                    "schedule_type": row["schedule_type"],
                }
            )

    payment_calendar = pd.DataFrame(calendar_rows).sort_values(["contract_id", "expected_payment_date"]).reset_index(drop=True)
    PAYMENT_CALENDAR_PATH.parent.mkdir(parents=True, exist_ok=True)
    payment_calendar.to_csv(PAYMENT_CALENDAR_PATH, index=False)
    return payment_calendar
