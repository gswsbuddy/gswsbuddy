import io
import traceback
import pandas as pd
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)


@app.route('/api/test_excel', methods=['POST', 'OPTIONS'])
@app.route('/', methods=['POST', 'OPTIONS'])
def process_sl_no():
  if request.method == 'OPTIONS':
    return '', 200

  if 'file' not in request.files:
    return jsonify({'error': 'No file uploaded.'}), 400

  file = request.files['file']

  try:
    # 1. Handle both native .xlsx and portal HTML-based .xls files
    try:
      df = pd.read_excel(file)
    except Exception:
      file.seek(0)
      html_content = file.read().decode('utf-8', errors='ignore')
      df = pd.read_html(html_content)[0]

    # 2. Insert Sl. No at position 0
    df.insert(0, 'Sl. No', range(1, len(df) + 1))

    # 3. Save to Excel stream
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
    # Catch crash details and return as JSON so JavaScript won't break
    error_details = traceback.format_exc()
    print(error_details)
    return jsonify({'error': str(e), 'traceback': error_details}), 500