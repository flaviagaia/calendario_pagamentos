from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from .config import CONTRACTS_DIR
from .sample_contracts import CONTRACT_TEMPLATES


def generate_contract_pdfs(output_dir: Path | None = None) -> list[Path]:
    output_dir = output_dir or CONTRACTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    body.leading = 16

    generated_paths: list[Path] = []
    for template in CONTRACT_TEMPLATES:
        pdf_path = output_dir / f"{template.contract_id}.pdf"
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, leftMargin=48, rightMargin=48, topMargin=48, bottomMargin=48)
        story = []
        for line in template.contract_text.split("\n\n"):
            story.append(Paragraph(line.replace("\n", "<br/>"), body))
            story.append(Spacer(1, 12))
        doc.build(story)
        generated_paths.append(pdf_path)
    return generated_paths
