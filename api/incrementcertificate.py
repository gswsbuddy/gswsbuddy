from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
# Import docx components according to your current system architecture dependencies
# e.g., from docx import Document ...

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        # 1. Gather properties out of payload dictionary
        scope = data.get('scope', 'RURAL').upper()
        name = data.get('name', '').strip() or "[Name Placeholder]"
        gender = data.get('gender', 'Male')
        designation = data.get('designation', '').strip() or "[Designation]"
        place_of_working = data.get('placeOfWorking', '').strip() or "[Secretariat]"
        mandal = data.get('mandal', '').strip() or "[Mandal]"
        district = data.get('district', '').strip() or "[District]"
        
        # Date Processing Setup
        joining_raw = data.get('dateOfJoining', '')
        reg_raw = data.get('regularisationDate', '')
        inc_raw = data.get('lastIncrementDate', '')
        
        def format_date(d_str):
            try:
                return datetime.strptime(d_str, '%Y-%m-%d').strftime('%d/%m/%Y')
            except:
                return "[Date]"

        date_of_joining = format_date(joining_raw)
        regularisation_date = format_date(reg_raw)
        last_increment_date = format_date(inc_raw)
        
        # Calculate dynamic loop date ceiling (+364 days offset)
        one_year_date = "[Date]"
        if inc_raw:
            try:
                dt = datetime.strptime(inc_raw, '%Y-%m-%d') + timedelta(days=364)
                one_year_date = dt.strftime('%d/%m/%Y')
            except:
                pass

        basic_pay = data.get('basicPay', '') or "[Amount]"

        # 2. Assign dynamic contextual naming parameters
        branding_label = "Swarna Gramam" if scope == "RURAL" else "Swarna Ward"
        authority_designation = "Panchayath Secretary (DDO)" if scope == "RURAL" else "Ward Administrative Secretary"

        title_prefix = "Sri" if gender == "Male" else "Smt"
        he_she = "He" if gender == "Male" else "She"
        his_her = "His" if gender == "Male" else "Her"

        # ... [Initialize your standard template Document settings here] ...

        # 3. Compile narrative paragraph blocks
        # narrative text constructs using branding_label ("Swarna Gramam" / "Swarna Ward")
        narrative_text = (
            f"This is to certify that {title_prefix} {name} working as {designation} "
            f"at {place_of_working} {branding_label}, {mandal} (M), {district} District "
            f"from {date_of_joining}. {he_she} has regularised from service on {regularisation_date}. "
            f"{his_her} basic pay is Rs. {basic_pay}/- wef {last_increment_date}. "
            f"{he_she} has completed one year of {his_her.lower()} service without any break. "
            f"{he_she} has paid and drawn salary for the period from {last_increment_date} to {one_year_date}."
        )
        
        # ... [Inject text and build the leave tracking tables matrix block using loops] ...

        # 4. Generate bottom alignment signature blocks
        # sig_run adds the verified authority designation and corporate scope location titles
        signature_block_text = (
            f"{authority_designation}\n"
            f"{place_of_working} {branding_label}\n"
            f"{mandal} (M.), {district} Dist."
        )

        # ... [Stream the file binary bytes array back as docx attachment stream response] ...