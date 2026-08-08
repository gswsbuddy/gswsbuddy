import io
import traceback
from flask import Flask, jsonify, request, send_file
import pandas as pd

app = Flask(__name__)


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
    # Read file stream
    file_bytes = file.read()

    # Try standard excel engine
    try:
      df = pd.read_excel(io.BytesIO(file_bytes))
    except Exception:
      # Lightweight fallback
      df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')

    # Remove existing Sl. No column if present
    existing_cols = [
        c
        for c in df.columns
        if str(c).strip().lower() in ['sl. no', 's.no', 'sl.no', 'sl no']
    ]
    if existing_cols:
      df.drop(columns=existing_cols, inplace=True)

    # Insert Sl. No at index 0
    df.insert(0, 'Sl. No', range(1, len(df) + 1))

    # Write to openpyxl stream
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
      df.to_excel(writer, index=False, sheet_name='Sheet1')
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