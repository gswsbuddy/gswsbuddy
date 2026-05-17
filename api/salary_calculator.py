from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        try:
            # Core inputs
            basic = float(params.get('basic', [0])[0])
            hra_rate = float(params.get('hra_rate', [0])[0])
            apgli = float(params.get('apgli', [0])[0])
            
            # Flexible deduction overrides (with official government defaults)
            gis_fund = float(params.get('gis', [15.00])[0])
            prof_tax = float(params.get('pt', [200.00])[0])
            ehs_sub = float(params.get('ehs', [225.00])[0])
            
            # 🔥 Dynamic DA Percentage Override (Defaults to current 37.31%)
            da_percent = float(params.get('da_rate', [37.31])[0])
        except (ValueError, TypeError):
            basic = 0.0
            hra_rate = 0.0
            apgli = 0.0
            gis_fund = 15.00
            prof_tax = 200.00
            ehs_sub = 225.00
            da_percent = 37.31

        # 1. Earnings Calculations
        hra = (hra_rate / 100.0) * basic
        da = (da_percent / 100.0) * basic
        total_earnings = basic + hra + da

        # 2. Deductions Calculations (CPS is strictly 10% of Basic + DA)
        cps = 0.10 * (basic + da)
        total_deductions = apgli + gis_fund + prof_tax + ehs_sub + cps

        # 3. Take-Home Net Output
        net_salary = total_earnings - total_deductions

        response_data = {
            "basic": basic,
            "hra_rate": hra_rate,
            "hra": hra,
            "da_percent": da_percent,
            "da": da,
            "total_earnings": total_earnings,
            "apgli": apgli,
            "gis": gis_fund,
            "pt": prof_tax,
            "ehs": ehs_sub,
            "cps": cps,
            "total_deductions": total_deductions,
            "net_salary": net_salary
        }

        # Serve the dynamically adjusted math back to the web browser
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())