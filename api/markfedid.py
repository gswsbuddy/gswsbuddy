from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        action = params.get('action', [None])[0]

        # 1. Safely load the secret DBT Pins database file
        try:
            with open('api/dbt pins.json', 'r') as f:
                data = json.load(f)
        except Exception:
            data = {}

        response_data = {}

        # Mode A: Safe dynamic suggestions (Returns matching names only, no credentials!)
        if action == "suggest":
            search_term = params.get('q', [''])[0].strip().lower()
            if search_term:
                matches = [
                    name for name in data.keys() 
                    if search_term in name.lower()
                ]
                response_data = matches[:15]  # Limit to top 15 results for speedy autocomplete
            else:
                response_data = []

        # Mode B: Fetch deep profile records for the chosen target RBK name
        elif action == "lookup":
            rbk_name = params.get('rbk', [''])[0].strip()
            
            if rbk_name in data:
                entry = data[rbk_name]
                response_data = {
                    "dealerId": entry.get("dealerId", "N/A"),
                    "agencyName": entry.get("agencyName", "N/A"),
                    "posPin": entry.get("posPin", "N/A")
                }
            else:
                response_data = {"error": "RSK నామం లభించలేదు. దయచేసి పేరు సరిచూసుకోండి."}
        
        else:
            response_data = {"error": "Invalid action parameters"}

        # 2. Serve neat response data package back to client
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())