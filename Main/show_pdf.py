from __future__ import annotations
from typing import List
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
import webbrowser
import os


def show_pdf(data: List, file_name: str):
    """
    Show the report PDF
    """

    file_name1 = file_name + ".pdf"
    file_name = "/{}".format(file_name1)
    pdf = SimpleDocTemplate(
        file_name,
        pagesize=letter,
        leftMargin=0,
        rightMargin=0,
        topMargin=5
    )

    pdf.build(data)
    # webbrowser.open_new(r'file_name')
    # messagebox.showinfo(title="Report Created", message="{} created on desktop".format(file_name1))
