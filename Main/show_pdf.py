from __future__ import annotations
from typing import List
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
import io

def show_pdf(data: List):
    """
    Show the report PDF
    """


    ######## The online version ###########
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




    #### The OFFFFFLINE VERSION #####3

    # file = "trial.pdf"
    # pdf = SimpleDocTemplate(
    #     file,
    #     pagesize=letter,
    #     leftMargin=0,
    #     rightMargin=0,
    #     topMargin=5
    # )

    # pdf.build(data)
    # # return (file, pdf)
