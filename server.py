#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import base64
import tempfile
import datetime
import jobber_parser
import receipt_parser
import spec_manual_finder

PORT = 8088
LOG_FILE = "/Users/corybaxter/Desktop/AI/projects/HVAC-partslist/live_debug.log"
SERVE_DIR = "/Users/corybaxter/Desktop/AI/projects/HVAC-partslist"

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class TelemetryHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/telemetry':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode('utf-8'))
                now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                level = payload.get('level', 'INFO').upper()
                event = payload.get('event', 'unknown')
                data = payload.get('data', {})
                data_str = json.dumps(data) if data else ""
                
                log_line = f"[{now}] [{level}] {event} | {data_str}\n"
                
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(log_line)
                    f.flush()
                
                print(log_line, end='', flush=True)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status":"logged"}')
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f'{{"error":"{str(e)}"}}'.encode('utf-8'))

        elif self.path == '/api/parse-jobber':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode('utf-8'))
                manual_text = payload.get('text', '').strip()
                image_b64 = payload.get('image', '')

                extracted_text = ""
                if manual_text:
                    extracted_text = manual_text
                elif image_b64:
                    # Strip base64 header if present (e.g. data:image/png;base64,...)
                    if ',' in image_b64:
                        image_b64 = image_b64.split(',', 1)[1]
                    raw_bytes = base64.b64decode(image_b64)
                    
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        tmp_file.write(raw_bytes)
                        tmp_path = tmp_file.name

                    try:
                        extracted_text = jobber_parser.run_vision_ocr(tmp_path)
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

                parsed_result = jobber_parser.parse_jobber_text(extracted_text)
                
                # Log telemetry
                now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                log_line = f"[{now}] [ACTION] OCR_JOBBER_PARSED | {{'title': '{parsed_result.get('title')}', 'tonnage': {parsed_result.get('tonnage')}, 'chars': {len(extracted_text)}}}\n"
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(log_line)
                    f.flush()
                print(log_line, end='', flush=True)

                response_data = {
                    "success": True,
                    "extracted_text": extracted_text,
                    "parsed": parsed_result
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            except Exception as e:
                print(f"Error parsing jobber: {e}", flush=True)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))

        elif self.path == '/api/parse-receipt':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode('utf-8'))
                manual_text = payload.get('text', '').strip()
                images_b64 = payload.get('images', [])
                if not images_b64 and payload.get('image'):
                    images_b64 = [payload.get('image')]

                extracted_text = manual_text
                if not extracted_text and images_b64:
                    all_texts = []
                    for img_b64 in images_b64:
                        if ',' in img_b64:
                            img_b64 = img_b64.split(',', 1)[1]
                        raw_bytes = base64.b64decode(img_b64)
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                            tmp_file.write(raw_bytes)
                            tmp_path = tmp_file.name
                        try:
                            t = receipt_parser.run_vision_ocr(tmp_path)
                            all_texts.append(t)
                        finally:
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                    extracted_text = "\n\n".join(all_texts)

                parsed_result = receipt_parser.parse_receipt_text(extracted_text)

                # Telemetry
                now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                log_line = f"[{now}] [ACTION] OCR_RECEIPT_PARSED | {{'supplier': '{parsed_result.get('supplier')}', 'items': {len(parsed_result.get('items', []))}}}\n"
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(log_line)
                    f.flush()
                print(log_line, end='', flush=True)

                response_data = {
                    "success": True,
                    "extracted_text": extracted_text,
                    "parsed": parsed_result
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
            except Exception as e:
                print(f"Error parsing receipt: {e}", flush=True)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))

        elif self.path == '/api/lookup-specs':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode('utf-8'))
                query_text = payload.get('query', '')
                brand = payload.get('brand', '')
                model = payload.get('model', '')
                tonnage = payload.get('tonnage', 2.5)
                furnace_btu = payload.get('furnace_btu', '60k')
                furnace_eff = payload.get('furnace_eff', '95%')

                specs_result = spec_manual_finder.lookup_equipment_specs(
                    query_text=query_text,
                    brand=brand,
                    model=model,
                    tonnage=tonnage,
                    furnace_btu=furnace_btu,
                    furnace_eff=furnace_eff
                )

                # Log telemetry
                now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                log_line = f"[{now}] [ACTION] MANUAL_SPEC_LOOKUP | {{'query': '{query_text}', 'model': '{specs_result.get('model_name')}', 'mopd': '{specs_result.get('mopd')}'}}\n"
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(log_line)
                    f.flush()
                print(log_line, end='', flush=True)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "specs": specs_result}).encode('utf-8'))
            except Exception as e:
                print(f"Error looking up specs: {e}", flush=True)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))

        elif self.path == '/api/scan-model-plate':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode('utf-8'))
                image_b64 = payload.get('image', '')
                if not image_b64:
                    raise ValueError("No image data provided")

                if ',' in image_b64:
                    image_b64 = image_b64.split(',', 1)[1]
                raw_bytes = base64.b64decode(image_b64)

                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    tmp_file.write(raw_bytes)
                    tmp_path = tmp_file.name

                extracted_text = ""
                try:
                    extracted_text = jobber_parser.run_vision_ocr(tmp_path)
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

                # Extract Model Number
                detected_model = ""
                text_clean = extracted_text.replace('\r', ' ')
                model_patterns = [
                    r'(?:MODEL|MOD|M\/N|MODEL NO|MODEL NUMBER|PROD NO)[:.\s]+([A-Z0-9\-_]{5,24})',
                    r'(?:CAT NO|CATALOG NO)[:.\s]+([A-Z0-9\-_]{5,24})',
                    r'\b(4A7A\w+|4TTR\w+|4TWX\w+|S9X1\w+|S8X1\w+|59TP\w+|58SB\w+|24SCA\w+|24VNA\w+|BOVA[-_0-9A-Z]+|BVA[-_0-9A-Z]+|EL296\w+|ML196\w+|GM9C\w+|GSX\w+|PUZ[-_0-9A-Z]+|MSZ[-_0-9A-Z]+)\b'
                ]
                for pat in model_patterns:
                    m = re.search(pat, text_clean, re.IGNORECASE)
                    if m:
                        detected_model = m.group(1).strip().upper()
                        break

                if not detected_model:
                    # Token search for typical alphanumeric HVAC codes
                    for line in text_clean.split('\n'):
                        for tok in line.strip().split():
                            clean_tok = re.sub(r'[^A-Z0-9\-]', '', tok.upper())
                            if 6 <= len(clean_tok) <= 22 and re.search(r'[A-Z]', clean_tok) and re.search(r'\d', clean_tok):
                                if not any(clean_tok.startswith(x) for x in ['SERIAL', 'SER', 'VOLT', 'HERTZ', 'PHASE', 'AMPS', 'WATTS']):
                                    detected_model = clean_tok
                                    break
                        if detected_model:
                            break

                # Query specs for detected model
                specs_result = spec_manual_finder.lookup_equipment_specs(
                    query_text=detected_model or extracted_text[:120],
                    model=detected_model
                )

                # Log telemetry
                now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                log_line = f"[{now}] [ACTION] SCANNED_DATA_PLATE | {{'detected_model': '{detected_model}', 'chars': {len(extracted_text)}}}\n"
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(log_line)
                    f.flush()
                print(log_line, end='', flush=True)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "model": detected_model,
                    "extracted_text": extracted_text[:400],
                    "specs": specs_result
                }).encode('utf-8'))
            except Exception as e:
                print(f"Error scanning data plate: {e}", flush=True)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))

        else:
            self.send_response(404)
            self.end_headers()

    def end_headers(self):
        # Disable browser caching of index.html so mobile Safari always gets the fresh updates
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format, *args):
        # Clean logging
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {self.client_address[0]} {format % args}", flush=True)

if __name__ == '__main__':
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n=== THREADED SERVER STARTED AT {datetime.datetime.now().isoformat()} ===\n")
        f.flush()

    server = ThreadedHTTPServer(("", PORT), TelemetryHandler)
    print(f"🚀 Threaded Telemetry Server running on port {PORT} at http://10.0.0.249:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
