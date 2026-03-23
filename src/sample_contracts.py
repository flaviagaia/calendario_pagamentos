from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContractTemplate:
    contract_id: str
    supplier_name: str
    contract_title: str
    start_date: str
    end_date: str
    expected_amount: float
    schedule_type: str
    contract_text: str


CONTRACT_TEMPLATES = [
    ContractTemplate(
        contract_id="CTR-001",
        supplier_name="Alfa Facilities Ltda.",
        contract_title="Prestação de serviços de manutenção predial",
        start_date="2026-01-01",
        end_date="2026-12-31",
        expected_amount=14850.00,
        schedule_type="monthly_fixed_day",
        contract_text="""
CONTRATO ADMINISTRATIVO CTR-001

CONTRATADA: Alfa Facilities Ltda.
OBJETO: Prestação continuada de serviços de manutenção predial nas unidades administrativas.
VIGÊNCIA: de 01/01/2026 até 31/12/2026.

CLÁUSULA SEXTA - DO PAGAMENTO
O pagamento mensal será realizado até o dia 10 de cada mês subsequente à prestação dos serviços,
mediante apresentação da nota fiscal e ateste do gestor do contrato.

VALOR MENSAL: R$ 14.850,00.
        """.strip(),
    ),
    ContractTemplate(
        contract_id="CTR-002",
        supplier_name="Beta Dados e Processos S.A.",
        contract_title="Suporte de processamento documental",
        start_date="2026-01-01",
        end_date="2026-12-31",
        expected_amount=23500.00,
        schedule_type="monthly_business_day",
        contract_text="""
INSTRUMENTO PARTICULAR CTR-002

Contratada: Beta Dados e Processos S.A.
Objeto: Suporte de processamento documental e indexação de arquivos.
Período contratual: 01/01/2026 a 31/12/2026.

Condição de pagamento:
Os pagamentos ocorrerão mensalmente no 5º dia útil do mês seguinte ao da competência,
desde que a documentação de cobrança esteja regular e validada pela área demandante.

Valor mensal estimado: R$ 23.500,00.
        """.strip(),
    ),
    ContractTemplate(
        contract_id="CTR-003",
        supplier_name="Gamma Cloud Solutions",
        contract_title="Licenciamento de plataforma analítica",
        start_date="2026-01-01",
        end_date="2026-12-31",
        expected_amount=61500.00,
        schedule_type="quarterly_fixed_day",
        contract_text="""
CONTRATO CTR-003

PARTES: Banco XYZ e Gamma Cloud Solutions.
OBJETO: Licenciamento de plataforma analítica e suporte premium.
VIGÊNCIA CONTRATUAL: 01/01/2026 a 31/12/2026.

CLÁUSULA DE REMUNERAÇÃO:
O faturamento será trimestral, com vencimento no dia 15 dos meses de março, junho,
setembro e dezembro, observadas as entregas previstas no plano de trabalho.

Valor de cada parcela trimestral: R$ 61.500,00.
        """.strip(),
    ),
    ContractTemplate(
        contract_id="CTR-004",
        supplier_name="Delta Segurança Digital",
        contract_title="Implantação de solução antifraude",
        start_date="2026-02-10",
        end_date="2026-12-31",
        expected_amount=98000.00,
        schedule_type="one_time_after_acceptance",
        contract_text="""
CONTRATO DE FORNECIMENTO CTR-004

Fornecedor: Delta Segurança Digital.
Objeto: Implantação de solução antifraude para canais eletrônicos.
Início do projeto: 10/02/2026.

Cláusula de pagamento:
O pagamento ocorrerá em parcela única, 30 (trinta) dias após o aceite definitivo da implantação,
formalizado por termo assinado pelo gestor do projeto em 20/03/2026.

Valor total da parcela única: R$ 98.000,00.
        """.strip(),
    ),
    ContractTemplate(
        contract_id="CTR-005",
        supplier_name="Epsilon Contact Center",
        contract_title="Atendimento especializado de backoffice",
        start_date="2026-01-01",
        end_date="2026-12-31",
        expected_amount=32100.00,
        schedule_type="monthly_fixed_day",
        contract_text="""
CONTRATO DE PRESTAÇÃO DE SERVIÇOS CTR-005

Contratada: Epsilon Contact Center.
Objeto: Atendimento especializado de backoffice para operações de pagamentos.
Prazo: 01/01/2026 a 31/12/2026.

Da forma de pagamento:
O valor devido será quitado mensalmente no dia 20 de cada mês, após o recebimento da nota fiscal,
do relatório de serviços prestados e da validação pela gerência responsável.

Preço mensal contratado: R$ 32.100,00.
        """.strip(),
    ),
]
