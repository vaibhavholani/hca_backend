import requests
import json
from Reports import report_select
from flask import jsonify


NPM_SERVER_PORT = 3001

sample_data = {'suppliers': '[{"id":1685,"name":"SAI TEX FAB"}]', 'parties': '[{"id":530,"name":"SAMUNDER SAREE CENTER (D.K)"}]', 'report': 'khata_report', 'from': '2022-09-03', 'to': '2023-09-03'}


def generate_report(data):
    report_data = report_select.make_report(data)
    return report_data


# Convert the data to a JSON string
data = generate_report(sample_data)
json_data = json.dumps(data)


# Send the GET request
url = f"http://localhost:{NPM_SERVER_PORT}/generate-pdf"
headers = {"Content-Type": "application/json"}
response = requests.post(url, data=json_data, headers=headers)


# Save the received PDF
with open(f"{data['title']}.pdf", "wb") as f:
    f.write(response.content)
