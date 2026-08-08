import io
import traceback
from flask import Flask, jsonify, request, send_file
import pandas as pd

app = Flask(__name__)


def parse_file_safely(file_storage):
  """Safely parses .xlsx or HTML-based .xls portal exports."""
  file_bytes = file_storage.read()

  # Attempt 1: Standard Excel reading
  try:
    return pd.read_excel(io.BytesIO(file_bytes))
  except Exception:
    pass

  # Attempt 2: Portal HTML-table reading (.xls format)
  try:
    html_str = file_bytes.decode('utf-8', errors='ignore')
    tables = pd.read_html(io.StringIO(html_str))
    return tables[0]
  except Exception as e:
    raise ValueError(f'Could not parse spreadsheet file: {str(e)}')


@app.route('/api/test_excel', methods=['POST', 'OPTIONS'])
@app.route('/', methods=['POST', 'OPTIONS'])
def process_sl_no():
  if request.method == 'OPTIONS':
    return '', 200

  if 'file' not in request.files:
    return jsonify({'error': 'No file uploaded in request.'}), 400

  file = request.files['file']
  if file.filename == '':
    return jsonify({'error': 'Empty file selected.'}), 400

  try:
    # Read dataframe cleanly
    df = parse_file_safely(file)

    # Insert Sl. No column at the beginning
    df.insert(0, 'Sl. No', range(1, len(df) + 1))

    # Export to memory stream using openpyxl
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
      df.to_excel(writer, index=False, sheet_name='Summary')
    output.seek(0)

    return send_file(
        output,
        mimetype=(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ),
        as_attachment=True,
        download_name='Processed_With_SlNo.xlsx',
    )

  except Exception as e:
    err_trace = traceback.format_exc()
    print(err_trace)
    return jsonify({'error': str(e), 'traceback': err_trace}), 500