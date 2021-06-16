from __future__ import annotations
from typing import List, Tuple
from Visualise import create_pdf
from API_Database import efficiency
from API_Database import retrieve_register_entry, retrieve_indivijual, retrieve_partial_payment
from Main import show_pdf


def payment_list(party_ids: List[int], supplier_ids: List[int], start_date: str, end_date: str) -> List:

    """
    Return a 2D list of all pdf elements for Khata Report
    """

    table_header = ("Bill Number", "Bill Amount", "Pending Amt.", "Date", "Pending Days", "Status")

    hr_line = create_pdf.create_horizontal_line()

    master_elements = [create_pdf.create_h1("Payment List Report"), hr_line]

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
            pl_data = retrieve_register_entry.get_payment_list_data(supplier_id, party_id,  start_date, end_date)
            if len(pl_data) == 0:
                add_table = False
            part_no_bill = retrieve_partial_payment.get_partial_payment(supplier_id, party_id)
            table_data = [table_header] + pl_data + total_bottom_column(pl_data, part_no_bill)
            table = create_pdf.create_table(table_data)
            create_pdf.add_table_border(table)
            create_pdf.add_alt_color(table, len(table_data))
            create_pdf.add_padded_header_footer_columns(table, len(table_data))
            create_pdf.add_footer(table, len(table_data))
            create_pdf.add_status_colour(table, table_data, 5)
            create_pdf.add_day_number_colour(table, table_data, 4)
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

    total_sum = 0
    pending_amount = 0
    for elements in data:
        total_sum += int(elements[1])
        pending_amount += float(elements[2])

    return [("Total ->", total_sum, str(pending_amount)),
            ("", "", "Part No-bill ->  " + str(part_no_bill))]


def execute(party_ids: List[int], supplier_ids: List[int], start_date: str, end_date: str):
    """
    Show the Report
    """
    data = payment_list(party_ids, supplier_ids, start_date, end_date)
    io_file, pdf = show_pdf.show_pdf(data)

    return (io_file, "")
