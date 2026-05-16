from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. The Waiter brings the search inputs from the web page
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        district = params.get('district', [None])[0]
        mandal = params.get('mandal', [None])[0]
        rbk = params.get('rbk', [None])[0]

        # 2. Open the hidden JSON fridge safely
        try:
            with open('api/rbkaccounts.json', 'r') as f:
                data = json.load(f)
        except Exception:
            data = []

        # 3. Look for the matching row
        match = None
        for row in data:
            # Checking if the row matches what the user searched for
            if row.get("District") == district and row.get("MANDAL") == mandal and row.get("RBK Name") == rbk:
                match = row
                break

        # 4. Prepare the neat data package to send back
        if match:
            response_data = {
                "account": match.get("Account Numbers"),
                "ifsc": match.get("IFSC code"),
                "sbu": match.get("SBU Name"),
                "status": "Success"
            }
        else:
            response_data = {"error": "No matching record found"}

        # 5. Serve the response back to the web browser
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())