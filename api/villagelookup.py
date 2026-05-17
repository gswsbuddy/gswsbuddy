from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        action = params.get('action', [None])[0]

        # 1. Safely load the Master Village Code Directory database file
        try:
            with open('api/VillageLookup.json', 'r') as f:
                data = json.load(f)
        except Exception:
            data = {}

        response_data = {}

        # Mode A: Extract cascading layout nodes for dropdown assembly
        if action == "get_dropdowns":
            dropdown_structure = {}
            for dist, mandals in data.items():
                dropdown_structure[dist] = {}
                for mandal, villages in mandals.items():
                    dropdown_structure[dist][mandal] = list(villages.keys())
            response_data = dropdown_structure

        # Mode B: Fetch deep metadata records for the selected target village
        elif action == "lookup_codes":
            district = params.get('district', [None])[0]
            mandal = params.get('mandal', [None])[0]
            village = params.get('village', [None])[0]
            
            try:
                response_data = data[district][mandal][village]
            except KeyError:
                response_data = {"error": "గ్రామ కోడ్‌ల సమాచారం లభించలేదు."}
        
        else:
            response_data = {"error": "Invalid request parameters"}

        # 2. Return clean database metrics plate to the layout stream
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())