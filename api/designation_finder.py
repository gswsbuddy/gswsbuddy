from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        action = params.get('action', [None])[0]

        # 1. Safely load the raw master directory list
        try:
            with open('api/annexrural1.json', 'r') as f:
                data = json.load(f)
        except Exception:
            data = {}

        response_data = {}

        # Action A: Build the dropdown menu mappings dynamically
        if action == "get_dropdowns":
            dropdown_structure = {"mapping": {}, "designations": []}
            designation_set = set()
            
            for dist, mandals in data.items():
                dropdown_structure["mapping"][dist] = {}
                for mandal, saches in mandals.items():
                    dropdown_structure["mapping"][dist][mandal] = list(saches.keys())
                    for sach_details in saches.values():
                        if "Designations" in sach_details:
                            designation_set.update(sach_details["Designations"].keys())
            
            dropdown_structure["designations"] = sorted(list(designation_set))
            response_data = dropdown_structure

        # Action B: Process specific designation row queries on the server
        elif action == "filter_by_designation":
            district = params.get('district', [None])[0]
            mandal = params.get('mandal', [None])[0]
            designation = params.get('designation', [None])[0]
            filter_val = params.get('filter', ['ALL'])[0]

            mandal_data = data.get(district, {}).get(mandal, {})
            results = []

            for sachivalayam, details in mandal_data.items():
                status = details.get("Designations", {}).get(designation, "NO")
                if (
                    filter_val == "ALL" or
                    (filter_val == "YES" and status == "YES") or
                    (filter_val == "NO" and status == "NO")
                ):
                    results.append({"name": sachivalayam, "approved": status})
            
            # Sort so YES positions float to the top
            results.sort(key=lambda x: x["approved"], reverse=True)
            response_data = results
        
        else:
            response_data = {"error": "Invalid request action parameters"}

        # 2. Serve the neat data package back to the waiter
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())