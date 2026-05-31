from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import io
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except Exception:
            self.send_error_response("Invalid request payload structures.")
            return

        name = data.get('name', '').strip() or "[Name Placeholder]"
        gender = data.get('gender', 'Male')
        designation = data.get('designation', '').strip() or "[Designation]"
        place_of_working = data.get('placeOfWorking', '').strip() or "[Secretariat]"
        mandal = data.get('mandal', '').strip() or "[Mandal]"
        district = data.get('district', '').strip() or "[District]"
        
        date_of_joining = self.format_date_indian(data.get('dateOfJoining', ''))
        regularisation_date = self.format_date_indian(data.get('regularisationDate', ''))
        basic_pay = data.get('basicPay', '').strip() or "[Amount]"
        
        last_inc_raw = data.get('lastIncrementDate', '')
        last_increment_date = self.format_date_indian(last_inc_raw)
        one_year_date = self.calculate_one_year_later(last_inc_raw)

        leaves_input = data.get('leaves', {})

        title_prefix = "Sri" if gender == "Male" else "Smt"
        he_she = "He" if gender == "Male" else "She"
        his_her = "His" if gender == "Male" else "Her"

        doc = Document()
        
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1.25)
            section.right_margin = Inches(1.25)

        style = doc.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(12)

        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_p.add_run("EMPLOYEE SERVICE CERTIFICATE")
        title_run.bold = True
        title_run.font.size = Pt(14)
        title_run.underline = True

        title_p.paragraph_format.space_after = Pt(24)

        body_p = doc.add_paragraph()
        # 👑 Restored back to your original 1.5 line height spacing parameters
        body_p.paragraph_format.line_spacing = 1.5
        body_p.paragraph_format.space_after = Pt(12)
        body_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        body_p.paragraph_format.first_line_indent = Inches(0.5)
        
        narrative = (
            f"This is to certify that {title_prefix} {name} working as {designation} "
            f"at {place_of_working} Grama Sachivalayam, {mandal} (M), {district} District "
            f"from {date_of_joining}. {he_she} has regularised from service on {regularisation_date}. "
            f"{his_her} basic pay is Rs. {basic_pay}/- wef {last_increment_date}. "
            f"{he_she} has completed one year of {his_her.lower()} service without any break. "
            f"{he_she} has paid and drawn salary for the period from {last_increment_date} to {one_year_date}."
        )
        body_p.add_run(narrative)

        intro_p = doc.add_paragraph()
        intro_p.paragraph_format.line_spacing = 1.5  # Restored paragraph line height
        intro_p.paragraph_format.space_after = Pt(6)  # Kept tight table box approach gap
        intro_p.add_run(f"{his_her} leave availed details are as follows from the period {last_increment_date} to {one_year_date}:")

        table = doc.add_table(rows=6, cols=6)
        table.style = 'Table Grid'
        
        headers = ["S. No", "Type of Leave", "From", "To", "Days", "Remarks"]
        hdr_cells = table.rows[0].cells
        for i, text in enumerate(headers):
            hdr_cells[i].text = text
            p = hdr_cells[i].paragraphs[0]
            p.runs[0].font.bold = True
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            if i != 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        leave_keys = [
            ("maternity", "Maternity Leave"),
            ("eol", "EOL - ExtraOrdinary Leave"),
            ("medical", "Medical Leave (HPL/Commuted)"),
            ("childcare", "Child Care Leave"),
            ("earned", "Earned Leave")
        ]
        
        for idx, (key, label) in enumerate(leave_keys, start=1):
            row_cells = table.rows[idx].cells
            row_cells[0].text = str(idx)
            row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            row_cells[1].text = label
            
            leave_data = leaves_input.get(key, {})
            is_availed = leave_data.get('availed', False)
            
            if is_availed:
                f_date = self.format_date_indian(leave_data.get('from', ''))
                t_date = self.format_date_indian(leave_data.get('to', ''))
                days = self.calculate_days_between(leave_data.get('from', ''), leave_data.get('to', ''))
                remarks = leave_data.get('remarks', '').strip() or "-"
                
                row_cells[2].text = f_date
                row_cells[3].text = t_date
                row_cells[4].text = str(days)
                row_cells[5].text = remarks
            else:
                row_cells[2].text = "NIL"
                row_cells[3].text = "NIL"
                row_cells[4].text = "NIL"
                row_cells[5].text = "-"

            for col_idx in [0, 2, 3, 4, 5]:
                p = row_cells[col_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)

        eligibility_p = doc.add_paragraph()
        eligibility_p.paragraph_format.space_before = Pt(12)  # Kept tight table box bottom approach gap
        eligibility_p.paragraph_format.line_spacing = 1.5  # 👑 Restored paragraph line height
        eligibility_p.add_run(f"So {title_prefix} {name}, {designation} is eligible for Annual Grade Increment wef {one_year_date} as per our records.")

        sig_p = doc.add_paragraph()
        sig_p.paragraph_format.space_before = Pt(40)
        sig_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        sig_run = sig_p.add_run(
            f"Panchayath Secretary (DDO)\n"
            f"{place_of_working} Village Secretariat\n"
            f"{mandal} (M.), {district} Dist."
        )
        sig_run.font.bold = True

        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        binary_output = file_stream.read()

        self.send_response(200)
        self.send_header('Content-type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        self.send_header('Content-Disposition', 'attachment; filename="Increment_Certificate.docx"')
        self.send_header('Content-Length', str(len(binary_output)))
        self.end_headers()
        self.wfile.write(binary_output)

    def format_date_indian(self, date_str):
        if not date_str: return "NIL"
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            return "NIL"

    def calculate_one_year_later(self, date_str):
        if not date_str: return "[Date]"
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            ts = dt.timestamp() + (364 * 86400)
            return datetime.fromtimestamp(ts).strftime("%d/%m/%Y")
        except ValueError:
            return "[Date]"

    def calculate_days_between(self, start_str, end_str):
        if not start_str or not end_str: return 0
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d")
            end = datetime.strptime(end_str, "%Y-%m-%d")
            delta = (end - start).days + 1
            return delta if delta > 0 else 0
        except ValueError:
            return 0

    def send_error_response(self, message):
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))