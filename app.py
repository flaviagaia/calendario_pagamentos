from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.agents import run_payment_agents
from src.config import AUDIT_CASES_PATH, EXTRACTED_CONTRACTS_PATH, PAYMENT_CALENDAR_PATH, PAYMENT_MONITORING_PATH
from src.contract_extraction import build_raw_contract_dataset, extract_contract_rules
from src.pdf_generation import generate_contract_pdfs
from src.payment_calendar import build_payment_calendar
from src.sample_payments import generate_sample_actual_payments
from src.monitoring import evaluate_payment_calendar


st.set_page_config(page_title="Calendário Inteligente de Pagamentos", layout="wide")
st.title("Calendário Inteligente de Pagamentos")
st.caption("Leitura de contratos em PDF, calendário de pagamentos e alertas para gerência e auditoria.")


@st.cache_data(show_spinner=False)
def run_demo_pipeline():
    generate_contract_pdfs()
    actual = generate_sample_actual_payments()
    raw = build_raw_contract_dataset()
    rules = extract_contract_rules(raw)
    calendar = build_payment_calendar(rules)
    monitoring, audit_cases = evaluate_payment_calendar(calendar, actual)
    outputs = run_payment_agents(monitoring, audit_cases)
    return rules, calendar, monitoring, outputs.audit_cases, outputs.alerts, outputs.mode


rules, calendar_df, monitoring_df, audit_cases_df, alerts_df, agent_mode = run_demo_pipeline()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Contratos", len(rules))
col2.metric("Regras extraídas", int((rules["extraction_status"] == "ok").sum()))
col3.metric("Alertas", len(alerts_df))
col4.metric("Casos de auditoria", len(audit_cases_df))

st.info(f"Execução de agentes em modo: `{agent_mode}`")

left, right = st.columns([1, 1])
with left:
    st.subheader("Tipos de agenda extraídos")
    st.bar_chart(rules["schedule_type"].value_counts())

with right:
    st.subheader("Status de monitoramento")
    st.bar_chart(monitoring_df["monitoring_status"].value_counts())

timeline = monitoring_df.copy()
timeline["expected_payment_date"] = pd.to_datetime(timeline["expected_payment_date"])
timeline_counts = timeline.groupby(timeline["expected_payment_date"].dt.date).size().rename("pagamentos_previstos")
st.subheader("Calendário esperado de pagamentos")
st.line_chart(timeline_counts)

st.subheader("Alertas para gerência")
st.dataframe(
    alerts_df[
        [
            "contract_id",
            "supplier_name",
            "expected_payment_date",
            "actual_payment_date",
            "monitoring_status",
            "justification",
            "manager_alert",
            "audit_escalation",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Casos encaminhados para auditoria")
if audit_cases_df.empty:
    st.success("Nenhum caso sem justificativa foi encaminhado para auditoria.")
else:
    st.dataframe(
        audit_cases_df[
            [
                "contract_id",
                "supplier_name",
                "expected_payment_date",
                "actual_payment_date",
                "monitoring_status",
                "audit_reason",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.subheader("Regras extraídas dos contratos")
st.dataframe(rules, use_container_width=True, hide_index=True)

with st.expander("Arquivos gerados pelo pipeline"):
    st.markdown(
        f"""
        - Regras extraídas: `{EXTRACTED_CONTRACTS_PATH}`
        - Calendário: `{PAYMENT_CALENDAR_PATH}`
        - Monitoramento: `{PAYMENT_MONITORING_PATH}`
        - Casos de auditoria: `{AUDIT_CASES_PATH}`
        """
    )
