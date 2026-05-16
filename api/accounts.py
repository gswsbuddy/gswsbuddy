from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        action = params.get('action', [None])[0]

        # 1. Load the underlying data from the vault securely
        try:
            with open('api/rbkaccounts.json', 'r') as f:
                data = json.load(f)
        except Exception:
            data = []

        response_data = {}

        # Job Type A: Provide only the dropdown setup schema (Completely safe, missing bank information)
        if action == "get_mapping":
            mapping_list = []
            for row in data:
                mapping_list.append({
                    "District": row.get("District"),
                    "MANDAL": row.get("MANDAL"),
                    "RBK Name": row.get("RBK Name")
                })
            response_data = mapping_list

        # Job Type B: Run specific lookup match for one record row and supply sensitive bank elements
        elif action == "lookup":
            district = params.get('district', [None])[0]
            mandal = params.get('mandal', [None])[0]
            rbk = params.get('rbk', [None])[0]

            match = None
            for row in data:
                if row.get("District") == district and row.get("MANDAL") == mandal and row.get("RBK Name") == rbk:
                    match = row
                    break

            if match:
                response_data = {
                    "account": match.get("Account Numbers"),
                    "ifsc": match.get("IFSC code"),
                    "sbu": match.get("SBU Name")
                }
            else:
                response_data = {"error": "No matching record found"}
        
        else:
            response_data = {"error": "Invalid request action"}

        # Return results to the application front window
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())