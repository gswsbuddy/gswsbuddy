from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        # Parse inputs cleanly from the query string
        emp_name = params.get('name', [''])[0].strip()
        dob_str = params.get('dob', [''])[0].strip()  # Expected: YYYY-MM-DD
        
        try:
            premium = float(params.get('premium', [0])[0])
        except (ValueError, TypeError):
            premium = 0.0

        if not dob_str or premium <= 0:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Missing required parameters."}).encode())
            return

        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d")
        except ValueError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid date format."}).encode())
            return

        # 1. Automatic Date Math: Retirement Date (Last day of month turning 62)
        retire_year = dob.year + 62
        retire_month = dob.month
        
        if retire_month == 12:
            last_day = 31
        else:
            last_day = (datetime(retire_year, retire_month + 1, 1) - datetime(retire_year, retire_month, 1)).days
        
        retirement_date = datetime(retire_year, retire_month, last_day)

        # 2. Compute Age Next Birthday at the point of calculation (Current active age step)
        current_date = datetime.now()
        calculated_age = current_date.year - dob.year
        if (current_date.month, current_date.day) < (dob.month, dob.day):
            calculated_age -= 1
        age_next_birthday = calculated_age + 1

        # 3. Mapped G.O.Ms.No.198 Factor Schedule (Sum Assured per Re. 1 Premium)
        factor_table = {
            21: 424.19, 22: 403.61, 23: 384.00, 24: 365.32, 25: 347.51,
            26: 330.52, 27: 314.32, 28: 298.87, 29: 284.11, 30: 270.03,
            31: 256.58, 32: 243.73, 33: 231.44, 34: 219.68, 35: 208.43,
            36: 197.65, 37: 187.31, 38: 177.38, 39: 168.52, 40: 159.98,
            41: 151.73, 42: 143.77, 43: 136.07, 44: 128.62, 45: 121.38,
            46: 114.36, 47: 107.71, 48: 101.22, 49: 94.88,  50: 88.65,
            51: 82.50,  52: 76.39,  53: 70.28,  54: 64.12,  55: 57.83,
            56: 51.34,  57: 44.55
        }

        # Safe boundaries fallback execution
        factor = factor_table.get(age_next_birthday, 270.03)
        if age_next_birthday < 21: factor = 424.19
        if age_next_birthday > 57: factor = 44.55

        # 4. Calculate remaining timelines from today up to retirement age milestone
        service_months = (retirement_date.year - current_date.year) * 12 + (retirement_date.month - current_date.month)
        if service_months < 0: service_months = 0
        service_years = service_months / 12.0

        # Run your 3 precise on-point financial formulas:
        total_deductions = premium * service_months
        sum_assured = premium * factor
        bonus = sum_assured * 0.10 * service_years
        total_maturity = sum_assured + bonus

        response_data = {
            "name": emp_name,
            "age_next_birthday": age_next_birthday,
            "service_months": service_months,
            "service_years": round(service_years, 2),
            "official_retirement_date": retirement_date.strftime("%d-%b-%Y"),
            "total_deductions": round(total_deductions, 2),
            "sum_assured": round(sum_assured, 2),
            "bonus": round(bonus, 2),
            "total_maturity": round(total_maturity, 2)
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))