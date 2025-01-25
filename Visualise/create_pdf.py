from __future__ import annotations
from typing import List, Tuple
from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import TableStyle, Paragraph, LongTable, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def create_table(table_data: List[Tuple]) -> LongTable:
    """
    Returns a table of the input data.
    """

    table = LongTable(table_data, spaceAfter=5, spaceBefore=5)
    return table


def create_h1(text: str) -> Paragraph:
    """
    Create the report heading of the input text
    """
    para = Paragraph(text, ParagraphStyle(name="Normal", fontName="Times-bold", fontSize=50, spaceAfter=50,
                                          alignment=TA_CENTER))
    return para


def create_h2(text: str) -> Paragraph:
    """
    Create the report sub-heading of the input text
    """
    para = Paragraph("""<b><u>{}</u></b>""".format(text), ParagraphStyle(name="Normal", fontName="Times-Roman",
                                                                         fontSize=16, spaceAfter=15,
                                                                         spaceBefore=5, alignment=TA_CENTER))
    return para


def create_h3(text: str) -> Paragraph:
    """
    Create the report sub-heading of the input text
    """
    para = Paragraph("""<u>{}</u>""".format(text), ParagraphStyle(name="Normal", fontName="Times-Roman", fontSize=14,
                                                                  spaceAfter=10,
                                                                  spaceBefore=5,
                                                                  alignment=TA_CENTER))
    return para


def create_header(name: str) -> Paragraph:
    """
    Create a header on the page
    """
    para = Paragraph("""<b><u>{}</u></b>""".format(name), ParagraphStyle(name="Normal", fontName="Times-Roman", fontSize=8,
                                                                         spaceAfter=4,
                                                                         spaceBefore=4,
                                                                         alignment=TA_RIGHT))
    return para


def create_horizontal_line():
    """
    Create horizontal line on the page
    """
    d = Drawing(100, 1)
    d.add(Line(0, 0, 1000, 0))
    return d


def new_page():
    """
    Shift to the new page
    """
    return PageBreak()


def add_table_border(table: LongTable) -> None:
    """
    Add border to a given table
    """
    # use ('BOX', (0, 0), (-1, -1), 2, colors.black) to make a box around the cells
    # use ('LINEBEFORE', (2, 1), (2, -1), 2, colors.red) to make a vertical line before cell
    # in the same way LINEABOVE, LINEBELOW, LINEAFTER can be used

    ts = TableStyle([
        ('GRID', (0, 0), (-1, -1), 2, colors.black)
    ])
    table.setStyle(ts)


def add_alt_color(table: LongTable, len_data: int) -> None:
    """
    Give alternate colour to consecutive rows
    """
    # Alternate Colors
    for x in range(1, len_data):
        if x % 2 == 0:
            bc = colors.burlywood
        else:
            bc = colors.beige

        ts = TableStyle([('BACKGROUND', [0, x], [-1, x], bc)])
        table.setStyle(ts)


def add_padded_header_footer_columns(table: LongTable, len_data: int) -> None:
    """
    Have bigger padded column Headers
    """
    table_style = TableStyle(
        [('BACKGROUND', (0, 0), (-1, 0), colors.wheat),
         ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
         ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
         ('FONTSIZE', (0, 0), (-1, 0), 10),
         ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
         ('BACKGROUND', (0, 1), (-1, 0), colors.beige)
         ]
    )

    table.setStyle(table_style)


def add_footer(table: LongTable, len_data: int):
    """
    Adding Footers to the table
    """

    table_style = TableStyle([('FONTNAME', (0, len_data - 2), (-1, len_data - 1), 'Courier-Bold'),
                              ('BACKGROUND', (0, len_data - 2), (-1, len_data - 1), colors.sandybrown)
                              ])
    table.setStyle(table_style)


def add_table_font(table: LongTable, font_name: str) -> None:
    """
    Add a font to the entire table
    """
    table_style = TableStyle([('FONTNAME', (0, 1), (-1, -3), font_name)])
    table.setStyle(table_style)


def add_status_colour(table: LongTable, table_data: List[Tuple], status_index: int) -> None:
    """
    Add colour co-ordinated status tags
    """
    for x in range(1, len(table_data)-2):

        if table_data[x][status_index] == "N":
            bc = colors.orangered
        elif table_data[x][status_index] == "P":
            bc = colors.cornflowerblue
        elif table_data[x][status_index] == "F":
            bc = colors.lightgreen
        elif table_data[x][status_index] == "G":
            bc = colors.darkgreen
        elif table_data[x][status_index] == "PG":
            bc = colors.purple
        else:
            bc = colors.burlywood

        ts = TableStyle(
            [('BACKGROUND', [status_index, x], [status_index, x], bc),
             ('TEXTCOLOR', [status_index, x], [status_index, x], colors.black)])

        table.setStyle(ts)


def add_days_colour(table: LongTable, table_data: List[Tuple]) -> None:
    """
    Add colour to the boxes on the basis of the number of days for pending payments
    """

    for elements in range(1, len(table_data)-1):

        if elements % 3 == 1:
            bc = colors.lightgreen
        elif elements % 3 == 2:
            bc = colors.yellow
        else:
            bc = colors.orangered

        ts = TableStyle(
            [('BACKGROUND', [1, elements], [3, elements], bc),
             ('TEXTCOLOR', [1, elements], [3, elements], colors.black)])

        table.setStyle(ts)


def add_day_number_colour(table: LongTable, table_data: List[Tuple], day_index) -> None:
    """
    Add colour for boxes to show the category for number of days left.
    """
    for x in range(1, len(table_data)-2):

        if table_data[x][day_index] < 40:
            bc = colors.lightgreen
        elif 40 <= table_data[x][day_index] <= 70:
            bc = colors.yellow
        elif table_data[x][day_index] > 70:
            bc = colors.orangered
        else:
            bc = colors.burlywood

        ts = TableStyle(
            [('BACKGROUND', [day_index, x], [day_index, x], bc),
             ('TEXTCOLOR', [day_index, x], [day_index, x], colors.black)])

        table.setStyle(ts)


def change_cell_color(table: LongTable, x: int, y: int, color: str) -> None:
    """
    Change the color of the cell in long table
    """
    if color == "green":
        color = colors.lightgreen
    elif color == "red":
        color = colors.orangered

    ts = TableStyle(
        [('BACKGROUND', [x, y], [x, y], color)])
    table.setStyle(ts)


def make_last_row_bold(table: LongTable, len_data: int):
    """
    Very simple to understand dude....
    """
    table_style = TableStyle([('FONTNAME', (0, len_data - 1), (-1, len_data - 1), 'Courier-Bold'),
                              ('BACKGROUND', (0, len_data - 1), (-1, len_data - 1), colors.sandybrown)
                              ])
    table.setStyle(table_style)
