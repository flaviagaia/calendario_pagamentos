from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


try:
    from crewai import Agent, Crew, Process, Task
except Exception:  # pragma: no cover - optional dependency for local/demo execution
    Agent = Crew = Process = Task = None


@dataclass
class AgentOutputs:
    alerts: pd.DataFrame
    audit_cases: pd.DataFrame
    mode: str


def _deterministic_agent_flow(payment_monitoring: pd.DataFrame, audit_cases: pd.DataFrame) -> AgentOutputs:
    alerts = payment_monitoring[payment_monitoring["needs_attention"]].copy()
    alerts["manager_alert"] = alerts.apply(
        lambda row: (
            f"Contrato {row['contract_id']} apresentou status {row['monitoring_status']} "
            f"na data prevista {row['expected_payment_date']:%Y-%m-%d}."
        ),
        axis=1,
    )
    alerts["audit_escalation"] = alerts.apply(
        lambda row: "Escalar para auditoria interna." if not row["has_justification"] else "Acompanhar justificativa com a gerência.",
        axis=1,
    )
    return AgentOutputs(alerts=alerts, audit_cases=audit_cases.copy(), mode="deterministic_fallback")


def run_payment_agents(payment_monitoring: pd.DataFrame, audit_cases: pd.DataFrame) -> AgentOutputs:
    if Agent is None or Crew is None or Task is None:
        return _deterministic_agent_flow(payment_monitoring, audit_cases)

    # Keep a deterministic fallback-like execution even when CrewAI is installed,
    # so the project runs without requiring LLM credentials during portfolio demos.
    return _deterministic_agent_flow(payment_monitoring, audit_cases)
