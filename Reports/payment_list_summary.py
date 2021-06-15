from __future__ import annotations
from typing import List, Tuple
from Visualise import create_pdf
from API_Database import efficiency
from API_Database import retrieve_register_entry, retrieve_indivijual
from Main import show_pdf


def payment_list_summary(party_ids: List[int], supplier_ids: List[int], start_date: str, end_date: str) -> List:

    """
    Return a 2D list of all pdf elements for payment list Report
    """

    table_header = ("Days", "Total Amount", "Total Pending Amount")

    hr_line = create_pdf.create_horizontal_line()

    master_elements = [create_pdf.create_h1("Payment List Summary"), hr_line]

    for party_id in party_ids:
        top_elements = []
        elements = []
        party_name = retrieve_indivijual.get_party_name_by_id(party_id)
        h2text = "Party Name: " + party_name
        top_elements.append(create_pdf.create_h2(h2text))
        top_elements.append(hr_line)
        filter_suppliers = efficiency.filter_out_supplier(party_id, supplier_ids)
        for supplier_id in filter_suppliers:
            add_table = True
            pl_summary_data = retrieve_register_entry.get_payment_list_summary_data(supplier_id, party_id, start_date, end_date)
            if len(pl_summary_data) == 0:
                add_table = False
            if add_table:
                table_data = [table_header]
                supplier_name = retrieve_indivijual.get_supplier_name_by_id(supplier_id)
                add_text = "Supplier Name: " + supplier_name
                elements.append(create_pdf.create_h3(add_text))
                pl_summary_insert = [(" ",) + x for x in pl_summary_data]
                temp = pl_summary_insert[0]
                pl_summary_insert[0] = ("Below 40", temp[1], temp[2])
                pl_summary_insert[1] = ("40-70", temp[1], temp[2])
                pl_summary_insert[2] = ("Above 70", temp[1], temp[2])
                table_data = table_data + pl_summary_insert + total_bottom_column(pl_summary_insert)
                table = create_pdf.create_table(table_data)
                create_pdf.add_table_border(table)
                create_pdf.add_alt_color(table, len(table_data))
                create_pdf.add_padded_header_footer_columns(table, len(table_data))
                create_pdf.add_days_colour(table, table_data)
                create_pdf.add_table_font(table, "Courier")
                elements.append(table)

        if len(elements) != 0:
            master_elements = master_elements + top_elements + elements
            master_elements.append(create_pdf.new_page())

    return master_elements


def total_bottom_column(data: List) -> List[Tuple]:
    """
    Add up all the values
    """
    total_sum = 0
    pending_sum = 0

    for elements in data:
        if elements[1] != " " and elements[1] != "-" and elements[1] is not None:
            total_sum += int(elements[1])
        if elements[2] != " " and elements[2] != "-" and elements[2] is not None:
            pending_sum += int(elements[2])

    return [("Total", total_sum, pending_sum)]


def execute(party_ids: List[int], supplier_ids: List[int], start_date: str, end_date: str):
    """
    Show the Report
    """
    data = payment_list_summary(party_ids, supplier_ids, start_date, end_date)
    show_pdf.show_pdf(data, "payment_list_summary")

