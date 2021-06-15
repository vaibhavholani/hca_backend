from __future__ import annotations
from typing import List
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
import io

def show_pdf(data: List):
    """
    Show the report PDF
    """

    file = io.BytesIO()
    pdf = SimpleDocTemplate(
        file,
        pagesize=letter,
        leftMargin=0,
        rightMargin=0,
        topMargin=5
    )

    pdf.build(data)
    return (file, pdf)
    # webbrowser.open_new(r'file_name')
    # messagebox.showinfo(title="Report Created", message="{} created on desktop".format(file_name1))
