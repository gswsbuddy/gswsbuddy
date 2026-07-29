import io
import os
from flask import Flask, jsonify, render_template, request, send_file
import pandas as pd

app = Flask(__name__, template_folder='../templates')


def load_spreadsheet(file_bytes, filename):
  """Loads standard Excel files or HTML-based .xls files from government portals."""
  try:
    return pd.read_excel(file_bytes)
  except Exception:
    file_bytes.seek(0)
    html_content = file_bytes.read().decode('utf-8', errors='ignore')
    tables = pd.read_html(html_content)
    return tables[0]


@app.route('/')
def home():
  return render_template('Mangoecropdata.html')


@app.route('/api/process', methods=['POST'])
def process_file():
  if 'file' not in request.files:
    return jsonify({'error': 'No file uploaded.'}), 400

  uploaded_file = request.files['file']
  if uploaded_file.filename == '':
    return jsonify({'error': 'Selected file is empty.'}), 400

  try:
    # Read file stream into memory
    file_bytes = io.BytesIO(uploaded_file.read())
    df = load_spreadsheet(file_bytes, uploaded_file.filename)

    # Standardize column headers
    df.columns = [str(c).strip() for c in df.columns]

    # Map columns flexibly
    khata_col = next((c for c in df.columns if 'khatha' in c.lower()), None)
    aadhaar_col = next((c for c in df.columns if 'aadhaar' in c.lower()), None)
    booking_col = next((c for c in df.columns if 'booking' in c.lower()), None)
    farmer_col = next((c for c in df.columns if 'farmer name' in c.lower()), None)
    father_col = next((c for c in df.columns if 'father name' in c.lower()), None)
    crop_col = next((c for c in df.columns if 'crop name' in c.lower()), None)
    survey_col = next((c for c in df.columns if 'survey' in c.lower()), None)
    area_col = next(
        (
            c
            for c in df.columns
            if 'area' in c.lower() or 'extent' in c.lower()
        ),
        None,
    )

    if not (khata_col and booking_col and crop_col and area_col):
      return (
          jsonify({
              'error': (
                  'Required columns (Khata, Booking ID, Crop Name, Area) not'
                  ' found.'
              )
          }),
          400,
      )

    # Clean numeric data & crop flags
    df['Is_Mango'] = df[crop_col].astype(str).str.strip().str.lower() == 'మామిడి'
    df[area_col] = pd.to_numeric(df[area_col], errors='coerce').fillna(0.0)

    group_cols = [khata_col]
    if aadhaar_col:
      group_cols.append(aadhaar_col)

    output_rows = []
    grouped = df.groupby(group_cols, dropna=False)

    for group_key, group in grouped:
      if isinstance(group_key, tuple):
        khata = group_key[0]
        aadhaar = group_key[1] if len(group_key) > 1 else ''
      else:
        khata = group_key
        aadhaar = ''

      farmer_name = (
          group[farmer_col].dropna().iloc[0]
          if (farmer_col and not group[farmer_col].dropna().empty)
          else ''
      )
      father_name = (
          group[father_col].dropna().iloc[0]
          if (father_col and not group[father_col].dropna().empty)
          else ''
      )

      # Deduplicate by Booking ID to prevent double counting
      if booking_col:
        unique_group = group.drop_duplicates(subset=[booking_col])
        total_land_extent = unique_group[area_col].sum()
      else:
        total_land_extent = group[area_col].sum()

      mango_rows = group[group['Is_Mango']]

      top2_surveys_str = 'N/A'
      mango_booking_id = 'N/A'
      max_plot_extent = 0.0
      total_mango_extent = 0.0
      all_surveys_list = []

      if not mango_rows.empty:
        if booking_col:
          unique_mango = mango_rows.drop_duplicates(subset=[booking_col])
        else:
          unique_mango = mango_rows

        total_mango_extent = unique_mango[area_col].sum()

        # Sort by plot extent descending
        sorted_mango = unique_mango.sort_values(by=area_col, ascending=False)

        max_mango_row = sorted_mango.iloc[0]
        mango_booking_id = max_mango_row[booking_col]
        max_plot_extent = max_mango_row[area_col]

        if survey_col:
          top_plots = [
              str(s).strip()
              for s in sorted_mango.head(2)[survey_col]
              if pd.notna(s) and str(s).strip() and str(s).strip() != 'N/A'
          ]
          if top_plots:
            top2_surveys_str = ', '.join(top_plots)

          all_surveys_list = [
              str(s).strip()
              for s in sorted_mango[survey_col].unique()
              if pd.notna(s) and str(s).strip() and str(s).strip() != 'N/A'
          ]

      mango_surveys = ', '.join(all_surveys_list) if all_surveys_list else 'N/A'

      output_rows.append({
          'Khatha No': khata,
          'Farmer Name': farmer_name,
          'Father Name': father_name,
          'Masked Aadhaar': aadhaar,
          'Max Mango Booking ID': mango_booking_id,
          'Max Plot Extent': max_plot_extent,
          'Top 2 Mango Surveys': top2_surveys_str,
          'All Mango Surveys': mango_surveys,
          'Mango Survey Count': len(all_surveys_list),
          'Total Land Extent': round(total_land_extent, 4),
          'Total Mango Extent': round(total_mango_extent, 4),
      })

    processed_df = pd.DataFrame(output_rows)

    # Output processed dataframe to Excel in-memory buffer
    output_stream = io.BytesIO()
    with pd.ExcelWriter(output_stream, engine='openpyxl') as writer:
      processed_df.to_excel(writer, index=False, sheet_name='Summary')
    output_stream.seek(0)

    return send_file(
        output_stream,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='Mango_Crop_Processed_Summary.xlsx',
    )

  except Exception as e:
    return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
  app.run(debug=True)