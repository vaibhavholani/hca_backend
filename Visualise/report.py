from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from Reports import supplier_register_report

data = supplier_register_report.khata_report_single_party_supplier(1, 1, "28/02/2019", "28/02/2019")

filename = "hello.pdf"

text = "I am the boss"

d = Drawing(100, 1)
d.add(Line(0, 0, 1000, 0))


pdf = SimpleDocTemplate(
    filename,
    pagesize=letter,
    leftMargin=0,
    rightMargin=0,
    topMargin=0
    )
print(type(pdf))
style = getSampleStyleSheet()

p_text = "KHATA REPORT"
para = Paragraph(p_text, ParagraphStyle(name="Normal",
                                        fontName="Times-bold",
                                        fontSize=50,
                                        spaceAfter=50,
                                        alignment=TA_CENTER
                                        ))

table_style = TableStyle(
    [('BACKGROUND', (0, 0), (-1, 0), colors.wheat),
     ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
     ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
     ('FONTSIZE', (0, 0), (-1, 0), 10),
     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
     ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
     ]
)

table = Table(data, spaceAfter=5, spaceBefore=5)

table.setStyle(table_style)

# Alternate Colors
len_data = len(data)
for x in range(1, len_data):
    if x % 2 == 0:
        bc = colors.burlywood
    else:
        bc = colors.beige

    ts = TableStyle([('BACKGROUND', [0, x], [-1, x], bc)])
    table.setStyle(ts)

# for x in range(1, len_data):
#
#     if data[x][6] == "N":
#         bc = colors.red
#     elif data[x][6] == "P":
#         bc = colors.blue
#     elif data[x][6] == "G":
#         bc = colors.green
#     elif data[x][6] == "PG":
#         bc = colors.purple
#     else:
#         bc = colors.burlywood
#
#     ts = TableStyle(
#         [('BACKGROUND', [x, 6], [x, -1], bc),
#          ('TEXTCOLOR', [x, 6], [x, -1], colors.whitesmoke)
#          ])
#
#     table.setStyle(ts)

# Adding Borders
ts = TableStyle([
    ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ('LINEBEFORE', (2, 1), (2, -1), 2, colors.red),
    # in the same way LINEABOVE, LINEBELOW, LINEAFTER can be used
    ('GRID', (0, 0), (-1, -1), 2, colors.black)
])

table.setStyle(ts)


elements = []
elements.append(para)
elements.append(d)
elements.append(table)


pdf.build(elements)


# use PageBreak() to go to a new page

