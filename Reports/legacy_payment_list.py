from __future__ import annotations
from typing import List, Tuple
from Visualise import create_pdf
from API_Database import efficiency
from API_Database import retrieve_register_entry, retrieve_indivijual, retrieve_partial_payment
from Main import show_pdf


def legacy_payment_list(party_ids: List[int], supplier_ids: List[int], start_date: str, end_date: str) -> List:
    """
    Return a 2D list of all pdf elements for Khata Report
    """

    table_header = ("Memo Number", "Amount", "Type", "Date",
                    "Over 70", "Under 70", "Under 40", "Bill Number", "Date")

    hr_line = create_pdf.create_horizontal_line()

    master_elements = [create_pdf.create_h1("Payment list"), hr_line]

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
            khata_data = retrieve_register_entry.legacy_payment_list(supplier_id, party_id, start_date, end_date)
            if len(khata_data) == 0:
                add_table = False
            part_no_bill = retrieve_partial_payment.get_partial_payment(supplier_id, party_id)
            table_data = [table_header] + khata_data + total_bottom_column(khata_data, part_no_bill)
            table = create_pdf.create_table(table_data)
            create_pdf.add_table_border(table)
            create_pdf.add_alt_color(table, len(table_data))
            create_pdf.add_padded_header_footer_columns(table, len(table_data))
            create_pdf.add_footer(table, len(table_data))
            # create_pdf.add_status_colour(table, table_data, 3)
            create_pdf.add_table_font(table, "Courier")
            if add_table:
                supplier_name = retrieve_indivijual.get_supplier_name_by_id(supplier_id)
                add_text = "Supplier Name: " + supplier_name
                elements.append(create_pdf.create_h3(add_text))
                elements.append(table)
        if len(elements) != 0:
            master_elements = master_elements + top_elements + elements
            master_elements.append(create_pdf.new_page())

    return master_elements


def total_bottom_column(data: List, part_no_bill: int) -> List[Tuple]:
    """
    Add up all the values
    """
    over70 = 0
    under70 = 0
    under40 =0
    memo_sum = 0

    for elements in data:
        if elements[4] != "-":
            over70 += int(elements[4])
        if elements[5] != '-':
            under70 += int(elements[5])
        if elements[6] != '-':
            under40 += int(elements[6])
        if elements[1] != '-':
            memo_sum += int(elements[1])

    return [("Total:", memo_sum,"", "", over70, under70, under40), ("", "", "", "Part No-bill ->", part_no_bill)]


def execute(party_ids: List[int], supplier_ids: List[int], start_date: str, end_date: str):
    """
    Show the Report
    """
    data = legacy_payment_list(party_ids, supplier_ids, start_date, end_date)
    io_file, pdf = show_pdf.show_pdf(data)

    return (io_file, "")

