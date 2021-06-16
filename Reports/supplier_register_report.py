from __future__ import annotations
from typing import List, Tuple
from Visualise import create_pdf
from Main import show_pdf
from API_Database import retrieve_register_entry, retrieve_indivijual, retrieve_partial_payment
from API_Database import efficiency


def supplier_register(party_ids: List[int], supplier_ids: List[int], start_date: str, end_date: str) -> List:
    """
    Returns a 2D list of all pdf elements for supplier register
    """

    table_header = ("Bill Number", "Bill Amount", "Pending Amount", "Bill Date",  "Status")

    hr_line = create_pdf.create_horizontal_line()

    master_elements = [create_pdf.create_h1("Supplier Register"), hr_line]

    for supplier_id in supplier_ids:
        top_elements = []
        elements = []
        supplier_name = retrieve_indivijual.get_supplier_name_by_id(supplier_id)
        h2text = "Supplier Name: " + supplier_name
        top_elements.append(create_pdf.create_h2(h2text))
        top_elements.append(hr_line)
        filter_parties = efficiency.filter_out_parties(supplier_id, party_ids)
        for party_id in filter_parties:
            add_table = True
            register_data = retrieve_register_entry.get_supplier_register_data(supplier_id, party_id, start_date, end_date)
            if len(register_data) == 0:
                add_table = False
            part_no_bill = retrieve_partial_payment.get_partial_payment(supplier_id, party_id)
            table_data = [table_header] + register_data + total_bottom_column(register_data, part_no_bill)
            table = create_pdf.create_table(table_data)
            create_pdf.add_table_border(table)
            create_pdf.add_alt_color(table, len(table_data))
            create_pdf.add_padded_header_footer_columns(table, len(table_data))
            create_pdf.add_footer(table, len(table_data))
            create_pdf.add_status_colour(table, table_data, 4)
            create_pdf.add_table_font(table, "Courier")
            if add_table:
                party_name = retrieve_indivijual.get_party_name_by_id(party_id)
                add_text = "Party Name: " + party_name
                elements.append(create_pdf.create_h3(add_text))
                elements.append(table)
        if len(elements) != 0:
            master_elements = master_elements + top_elements + elements
            master_elements.append(create_pdf.new_page())

    return master_elements


def total_bottom_column(data: List, part_no_bill:int) -> List[Tuple]:
    """
    Add up all the values
    """
    total_sum = 0
    pending_sum = 0
    partial_sum = 0

    for elements in data:
        total_sum += int(elements[1])
        pending_sum += float(elements[2])

    return [("Total->", total_sum, pending_sum),
            ("", "", "Part No-Bill-> " + str(part_no_bill))]


def execute(party_ids: List[int], supplier_ids: List[int], start_date: str, end_date: str):
    """
    Show the Report
    """
    data = supplier_register(party_ids, supplier_ids, start_date, end_date)
    io_file, pdf = show_pdf.show_pdf(data)

    return (io_file, "")