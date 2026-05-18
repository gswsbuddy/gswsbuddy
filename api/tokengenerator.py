from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import io

# Import the core Word processing engine components
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        # 1. Parse incoming parameters with safe default fallbacks
        rsk = params.get('rsk', ['Unknown RBK'])[0].strip()
        mandal = params.get('mandal', ['Unknown Mandal'])[0].strip()
        raw_date = params.get('date', [''])[0].strip()
        
        try:
            token_count = int(params.get('count', [100])[0])
            if token_count > 500: token_count = 500 # Strict upper bound safety cap
        except (ValueError, TypeError):
            token_count = 100

        # Format date smoothly from YYYY-MM-DD to DD-MMM-YYYY
        try:
            date_obj = datetime.strptime(raw_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d-%b-%Y")
        except Exception:
            formatted_date = raw_date

        # 2. Build the Document Layout
        doc = Document()
        
        # Set standardized crisp margin structures (A4 dimensions setup)
        sections = doc.sections
        for section in sections:
            section.page_width = Inches(8.27)
            section.page_height = Inches(11.69)
            section.top_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)

        token_index = 1

        # Process grid token blocks till the target token index is fully satisfied
        while token_index <= token_count:
            # Create a localized 4 Rows x 3 Columns token card layout table grid on the active page
            table = doc.add_table(rows=4, cols=3)
            table.alignment = WD_ALIGN_PARAGRAPH.CENTER
            table.autofit = False

            for row_idx in range(4):
                # Set explicit strict token row cutting boundary dimension metrics (~3.3cm)
                row = table.rows[row_idx]
                row.height = Inches(1.3)
                
                for col_idx in range(3):
                    cell = row.cells[col_idx]
                    cell.width = Inches(2.42) # Uniform distribution across standard margins
                    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

                    if token_index <= token_count:
                        # Clear any implicit system default block spaces
                        p = cell.paragraphs[0]
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p.paragraph_format.space_after = Pt(2)
                        p.paragraph_format.space_before = Pt(2)
                        p.paragraph_format.line_spacing = 1.0

                        # Text Line 1: Header title sequence
                        run1 = p.add_run(f"Urea Distribution – {formatted_date}\n")
                        run1.font.name = 'Arial'
                        run1.font.size = Pt(8)
                        run1.font.bold = True

                        # Text Line 2: Giant localized numeric block index allocation
                        run2 = p.add_run(f"{token_index}\n")
                        run2.font.name = 'Arial'
                        run2.font.size = Pt(20)
                        run2.font.bold = True

                        # Text Line 3: Signature baseline placeholders
                        run3 = p.add_run("Signature of VAA / MAO\n")
                        run3.font.name = 'Arial'
                        run3.font.size = Pt(10)
                        run3.font.bold = True

                        # Text Line 4 & 5: Descriptive local organizational tracking nodes
                        run4 = p.add_run(f"{rsk} RSK\n")
                        run4.font.name = 'Arial'
                        run4.font.size = Pt(10)
                        run4.font.bold = True

                        run5 = p.add_run(f"{mandal} Mandal")
                        run5.font.name = 'Arial'
                        run5.font.size = Pt(11)
                        run5.font.bold = True

                        token_index += 1
                    else:
                        # Append structurally empty silent spacers to fill grid padding cleanly
                        p = cell.paragraphs[0]
                        p.text = ""

            # Inject clean system page-breaks to separate batch token clusters neatly
            if token_index <= token_count:
                doc.add_page_break()

        # 3. Save Compiled File binary stream straight to Vercel gateway stream out pipeline
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        binary_data = file_stream.read()

        # Stream binary file back directly into the browser downloader line
        clean_filename = f"{rsk.replace(' ', '_')}_Tokens.docx"
        self.send_response(200)
        self.send_header('Content-type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        self.send_header('Content-Disposition', f'attachment; filename="{clean_filename}"')
        self.end_headers()
        self.wfile.write(binary_data)