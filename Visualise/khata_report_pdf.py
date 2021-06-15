from __future__ import annotations
from typing import List
from Reports import supplier_register_report
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter


def show_pdf(data: List):
    """
    Show the khata report PDF
    """
    pdf = SimpleDocTemplate(
        "khata_report.pdf",
        pagesize=letter,
        leftMargin=0,
        rightMargin=0,
        topMargin=0
    )

    pdf.build(data)