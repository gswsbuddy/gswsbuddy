from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        action = params.get('action', [None])[0]

        try:
            with open('api/annexrural1.json', 'r') as f:
                data = json.load(f)
        except Exception:
            data = {}

        response_data = {}

        # Mode A: Provide dropdown mapping (Modified to also include designations dynamically!)
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

        # Mode B & C stay exactly the same as yesterday...
        elif action == "lookup_by_name":
            district = params.get('district', [None])[0]
            mandal = params.get('mandal', [None])[0]
            secretariat = params.get('secretariat', [None])[0]
            try:
                response_data = data[district][mandal][secretariat]
            except KeyError:
                response_data = {"error": "Not found."}

        elif action == "lookup_by_code":
            target_code = params.get('code', [None])[0]
            found = False
            for dist, mandals in data.items():
                for mandal, saches in mandals.items():
                    for sach_name, details in saches.items():
                        if str(details.get("Seccretariat Code")) == str(target_code):
                            response_data = {"sachivalayam": sach_name, "district": dist, "mandal": mandal, "type": details.get("Rural / Urban"), "category": details.get("Population Category"), "designations": details.get("Designations"), "code": target_code}
                            found = True
                            break
                    if found: break
                if found: break
            if not found: response_data = {"error": "Code not found."}

        # 🔥 NEW MODE D: Designation Filter
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
                    (filter_val == "YES" && status == "YES") or
                    (filter_val == "NO" && status == "NO")
                ):
                    results.append({"name": sachivalayam, "approved": status})
            
            # Sort results with YES on top
            results.sort(key=lambda x: x["approved"], reverse=True)
            response_data = results

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())