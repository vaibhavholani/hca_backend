import requests
import json
from Reports import report_select
from flask import Flask, jsonify, request
from psql import execute_query
from Exceptions import DataError
import os
NPM_SERVER_PORT = 3001
sample_data = {'suppliers': '[{"id":1685,"name":"SAI TEX FAB"}]', 'parties': '[{"id":530,"name":"SAMUNDER SAREE CENTER (D.K)"}]', 'report': 'khata_report', 'from': '2022-09-03', 'to': '2023-09-03'}

def generate_report(data):
    """Generates a report by calling report_select.make_report with provided data and returns the report."""
    report_data = report_select.make_report(data)
    return report_data
app = Flask(__name__)

@app.errorhandler(DataError)
def handle_data_error(e):
    """Formats an error into a JSON response (with a 500 status) and prints error details."""
    error = e.dict()
    if error['status'] == 'error' and 'input_errors' not in error:
        error['input_errors'] = {}
    print('returning error')
    print(error)
    return (jsonify(error), 500)

@app.route('/execute_query', methods=['POST'])
def execute_query_route():
    """Extracts a query from a JSON request, executes it, and returns the result as a JSON response."""
    data = request.get_json()
    query = data['query']
    result = execute_query(query)
    return jsonify(result)

@app.route('/test_route', methods=['POST', 'GET'])
def test_route():
    """Generates a PDF from report data by calling an external service, saves the PDF locally, and returns a success message."""
    data = generate_report(sample_data)
    json_data = json.dumps(data)
    url = f'http://localhost:{NPM_SERVER_PORT}/generate-pdf'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json_data, headers=headers)
    with open(f"{data['title']}.pdf", 'wb') as f:
        f.write(response.content)
    return jsonify({'message': 'PDF generated successfully!'})
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)