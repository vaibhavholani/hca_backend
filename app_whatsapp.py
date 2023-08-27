import requests
import json

data = {'title': 'Khata Report', 'from': '2023-06-19', 'to': '2023-06-19', 'headings': [{'title': 'Party Name: test_party15', 'subheadings': [{'title': 'Supplier Name: test_supplier15', 'dataRows': [{'bill_no': 123456, 'bill_date': '19/06/2023', 'bill_amt': '5,000', 'bill_status': 'N', 'memo_no': '', 'memo_amt': '', 'memo_date': '', 'chk_amt': '', 'memo_type': ''}], 'specialRows': [{'name': 'Subtotal', 'value': '5,000', 'column': 'bill_amt', 'numeric': 5000, 'beforeData': False}, {'name': 'Subtotal', 'value': '0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {
    'name': '0.00% GR (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': '0.00% Less (-)', 'value': '- 0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Total Paid (=)', 'value': '0', 'column': 'memo_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Paid+GR (-)', 'value': '- 0', 'column': 'bill_amt', 'numeric': 0, 'beforeData': False}, {'name': 'Pending (=)', 'value': '5,000', 'column': 'bill_amt', 'numeric': 5000, 'beforeData': False}], 'displayOnIndex': True}]}]}

# Convert the data to a JSON string
json_data = json.dumps(data)

# URL-encode the JSON string
encoded_data = requests.utils.quote(json_data)

# Send the GET request
url = f"http://localhost:3000/generate-pdf?data={encoded_data}"
response = requests.get(url)

# Save the received PDF
with open(f"{data['title']}.pdf", "wb") as f:
    f.write(response.content)
