from __future__ import annotations

from src.agents import run_payment_agents
from src.contract_extraction import build_raw_contract_dataset, extract_contract_rules
from src.pdf_generation import generate_contract_pdfs
from src.payment_calendar import build_payment_calendar
from src.sample_payments import generate_sample_actual_payments
from src.monitoring import evaluate_payment_calendar


def main() -> None:
    generate_contract_pdfs()
    actual_payments = generate_sample_actual_payments()
    raw_contracts = build_raw_contract_dataset()
    contract_rules = extract_contract_rules(raw_contracts)
    payment_calendar = build_payment_calendar(contract_rules)
    payment_monitoring, audit_cases = evaluate_payment_calendar(payment_calendar, actual_payments)
    agent_outputs = run_payment_agents(payment_monitoring, audit_cases)

    print("Calendario Inteligente de Pagamentos")
    print("-" * 48)
    print(f"Contratos processados: {len(contract_rules)}")
    print(f"Regras extraidas com sucesso: {int((contract_rules['extraction_status'] == 'ok').sum())}")
    print(f"Eventos no calendario: {len(payment_calendar)}")
    print(f"Pagamentos monitorados: {len(payment_monitoring)}")
    print(f"Alertas para gerencia: {len(agent_outputs.alerts)}")
    print(f"Casos para auditoria: {len(agent_outputs.audit_cases)}")
    print(f"Modo dos agentes: {agent_outputs.mode}")


if __name__ == "__main__":
    main()
