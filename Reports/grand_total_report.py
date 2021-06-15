from __future__ import annotations
from typing import List, Tuple
from Visualise import create_pdf
from API_Database import retrieve_register_entry, retrieve_indivijual
from API_Database import efficiency
from Main import show_pdf


def grand_total_report(party_ids: List[int], supplier_ids: List[int], start_date: str, end_date: str) -> List:

    """
    Return a 2D list of all pdf elements for grand total Report
    """

    table_header = ("Party Name", "Total Work")

    hr_line = create_pdf.create_horizontal_line()

    master_elements = [create_pdf.create_h1("Grand Total"), hr_line]

    table_data = [table_header]

    for party_id in party_ids:
        party_name = retrieve_indivijual.get_party_name_by_id(party_id)
        total_work = 0
        filter_suppliers = efficiency.filter_out_supplier(party_id, supplier_ids)
        for supplier_id in filter_suppliers:
            grand_total_work = retrieve_register_entry.grand_total_work(supplier_id, party_id, start_date, end_date)
            total_work += int(grand_total_work)
        table_data.append((party_name, total_work))

    table_data.append(total_bottom_column(table_data))
    table = create_pdf.create_table(table_data)
    create_pdf.add_table_border(table)
    create_pdf.add_alt_color(table, len(table_data))
    create_pdf.add_padded_header_footer_columns(table, len(table_data))
    create_pdf.add_table_font(table, "Courier")
    create_pdf.make_last_row_bold(table, len(table_data))
    master_elements.append(table)
    return master_elements


def total_bottom_column(data: List) -> Tuple:
    """
    Add up all the values
    """
    total_sum = 0

    for x in range(1, len(data)):
        elements = data[x]
        total_sum += int(elements[1])

    return "Total", str(total_sum),


def execute(party_ids: List[int], supplier_ids: List[int], start_date: str, end_date: str):
    """
    Show the Report
    """
    data = grand_total_report(party_ids, supplier_ids, start_date, end_date)
    show_pdf.show_pdf(data, "grand_total_report")
