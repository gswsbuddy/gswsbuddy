from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        action = params.get('action', [None])[0]

        # 1. Load the structured urban directory safely behind the scenes
        try:
            with open('api/annexurban1.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            data = {}

        response_data = {}

        # Mode A: Provide only the dropdown choices structure (No heavy payload overhead)
        if action == "get_dropdowns":
            dropdown_structure = {}
            for dist, mandals in data.items():
                dropdown_structure[dist] = {}
                for mandal, saches in mandals.items():
                    dropdown_structure[dist][mandal] = list(saches.keys())
            response_data = dropdown_structure

        # Mode B: Name Lookup
        elif action == "lookup_by_name":
            district = params.get('district', [None])[0]
            mandal = params.get('mandal', [None])[0]
            secretariat = params.get('secretariat', [None])[0]
            
            try:
                response_data = data[district][mandal][secretariat]
            except KeyError:
                response_data = {"error": "Urban Secretariat details not found."}

        # Mode C: Code Lookup (Flattens the file instantly on demand matching your exact output keys)
        elif action == "lookup_by_code":
            target_code = params.get('code', [None])[0]
            found = False
            
            for dist, mandals in data.items():
                for mandal, saches in mandals.items():
                    for sach_name, details in saches.items():
                        # Read the exact code identifier from your new urban data schema
                        if str(details.get("Ward sachivalayam Code")) == str(target_code):
                            response_data = {
                                "sachivalayam": sach_name,
                                "district": dist,
                                "mandal": mandal,
                                "type": details.get("Rural / Urban"),
                                "category": details.get("Population Category"),
                                "designations": details.get("Designations"),
                                "code": target_code,
                                "ward_id": details.get("Ward ID")  # Includes the unique urban identifier field
                            }
                            found = True
                            break
                    if found: break
                if found: break
            
            if not found:
                response_data = {"error": "Urban Ward Secretariat code not found."}

        # Send clean JSON response back to the frontend waiter
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode('utf-8'))