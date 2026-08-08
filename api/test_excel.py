import io
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
    # 1. Read the Excel file into pandas
    df = pd.read_excel(file)

    # 2. Insert Sl. No at the beginning (1, 2, 3...)
    df.insert(0, 'Sl. No', range(1, len(df) + 1))

    # 3. Export to openpyxl memory buffer
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
        download_name='Processed_Names_With_SlNo.xlsx',
    )
  except Exception as e:
    return jsonify({'error': str(e)}), 500