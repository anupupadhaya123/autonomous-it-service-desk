"""
Autonomous IT Service Desk (AITSD) - Web Dashboard Server
Lightweight Python standard library HTTP server for the Enterprise IT Dashboard.
Zero external dependencies required.
"""

import sys
import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Ensure project root is in Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

from main import AutonomousITServiceDesk

# Initialize the system once at startup
service_desk = AutonomousITServiceDesk()

WEB_DIR = os.path.join(PROJECT_ROOT, "web")


class ITServiceDeskHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler serving static frontend assets and REST API endpoints"""

    def _set_headers(self, content_type="application/json", status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(status=204)

    def do_GET(self):
        parsed_path = urlparse(self.path).path

        # 1. API: Scenarios
        if parsed_path == "/api/scenarios":
            scenarios = [
                {
                    "id": "p1",
                    "title": "P1 Domain Controller Outage",
                    "content": "URGENT: Active Directory domain controller dc01.corp.internal is completely unresponsive. Over 400 employees across all departments are locked out and production systems cannot authenticate users. This is a complete company-wide outage!"
                },
                {
                    "id": "ransomware",
                    "title": "Ransomware Alert (LockBit)",
                    "content": "ALERT: An employee on finance workstation ws-fin-04 opened an email attachment named 'Invoice_March.exe' and now their screen shows a LockBit ransomware note saying all corporate files are encrypted. Bitcoin ransom demanded immediately!"
                },
                {
                    "id": "bsod",
                    "title": "Windows BSOD (0x000000ef)",
                    "content": "My Dell Latitude laptop has blue screened 3 times this morning with stop code 0x000000ef (CRITICAL_PROCESS_DIED). It keeps rebooting into Windows Recovery. Need assistance as I cannot attend client meetings."
                },
                {
                    "id": "vpn",
                    "title": "GlobalProtect VPN Failure",
                    "content": "Hello IT helpdesk, my GlobalProtect VPN client is failing to connect with 'Gateway not reachable' error when working remotely from home. I have tried restarting my laptop twice."
                },
                {
                    "id": "provisioning",
                    "title": "DevOps Laptop Provisioning",
                    "content": "Service request: Please provision new hire laptop and accounts for Alex Rivera (Senior Cloud Engineer) starting next Monday. Needs 32GB MacBook Pro, AWS production IAM access, and GitHub Enterprise organization invite."
                }
            ]
            self._set_headers("application/json")
            self.wfile.write(json.dumps(scenarios).encode("utf-8"))
            return

        # 2. Static File Routing
        if parsed_path == "/" or parsed_path == "/index.html":
            file_path = os.path.join(WEB_DIR, "index.html")
            content_type = "text/html; charset=utf-8"
        elif parsed_path == "/style.css":
            file_path = os.path.join(WEB_DIR, "style.css")
            content_type = "text/css; charset=utf-8"
        elif parsed_path == "/app.js":
            file_path = os.path.join(WEB_DIR, "app.js")
            content_type = "application/javascript; charset=utf-8"
        else:
            self._set_headers("text/plain", 404)
            self.wfile.write(b"404 Not Found")
            return

        if os.path.exists(file_path):
            self._set_headers(content_type)
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self._set_headers("text/plain", 404)
            self.wfile.write(b"File not found")

    def do_POST(self):
        parsed_path = urlparse(self.path).path

        if parsed_path == "/api/process":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(post_data)

                ticket_content = payload.get("content", "").strip()
                if not ticket_content:
                    self._set_headers("application/json", 400)
                    self.wfile.write(json.dumps({"error": "Ticket content cannot be empty"}).encode("utf-8"))
                    return

                # Execute multi-agent support pipeline
                results = service_desk.process_ticket(ticket_content)

                self._set_headers("application/json")
                self.wfile.write(json.dumps(results).encode("utf-8"))

            except Exception as e:
                self._set_headers("application/json", 500)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self._set_headers("text/plain", 404)
            self.wfile.write(b"Endpoint not found")

    def log_message(self, format, *args):
        """Clean HTTP access logging"""
        sys.stderr.write(f"[HTTP] {self.address_string()} - {format % args}\n")


def run_server(port=5000, open_browser=True):
    """Start the web server and open the browser"""
    server_address = ("", port)
    httpd = HTTPServer(server_address, ITServiceDeskHandler)
    url = f"http://localhost:{port}"

    print("="*80)
    print(f"AUTONOMOUS IT SERVICE DESK (AITSD) - WEB DASHBOARD")
    print(f"Server running at: {url}")
    print("Press Ctrl+C to stop the server.")
    print("="*80 + "\n")

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web dashboard server...")
        httpd.server_close()


if __name__ == "__main__":
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    # Don't auto-open browser if --no-browser flag passed
    open_b = "--no-browser" not in sys.argv
    run_server(port=port, open_browser=open_b)
