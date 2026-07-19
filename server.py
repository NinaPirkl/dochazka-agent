"""
Docházka Agent — lokální proxy server
Spouští se přes spustit_agenta.bat nebo spustit_agenta.sh
"""

import http.server
import json
import urllib.request
import urllib.error
import base64
import os
import sys
import webbrowser
import threading

PORT = 8080
HTML_FILE = "dochazka_agent.html"

class ProxyHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Potlač výpis každého requestu
        pass

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, Accept")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        # Odeslat HTML soubor
        if self.path == "/" or self.path == f"/{HTML_FILE}":
            try:
                with open(HTML_FILE, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"dochazka_agent.html not found")
            return

        # Proxy GET requesty na Jira
        if self.path.startswith("/jira/"):
            jira_path = self.path[6:]  # odstraň /jira/
            auth = self.headers.get("X-Jira-Auth", "")
            self._proxy_jira("GET", jira_path, auth)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        # Proxy POST requesty na Jira
        if self.path.startswith("/jira/"):
            jira_path = self.path[6:]
            auth = self.headers.get("X-Jira-Auth", "")
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else None
            self._proxy_jira("POST", jira_path, auth, body)
            return

        self.send_response(404)
        self.end_headers()

    def _proxy_jira(self, method, path, auth, body=None):
        url = f"https://packeta.atlassian.net{path}"
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())


def open_browser():
    import time
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}/{HTML_FILE}")


if __name__ == "__main__":
    # Zkontroluj že HTML soubor existuje
    if not os.path.exists(HTML_FILE):
        print(f"CHYBA: {HTML_FILE} nenalezen ve stejné složce jako server.py")
        input("Stiskni Enter pro ukončení...")
        sys.exit(1)

    print(f"Docházka Agent běží na http://localhost:{PORT}/{HTML_FILE}")
    print("Zavři toto okno až skončíš.\n")

    # Otevři prohlížeč po 1 sekundě
    threading.Thread(target=open_browser, daemon=True).start()

    try:
        server = http.server.HTTPServer(("", PORT), ProxyHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer zastaven.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {PORT} je již obsazen. Zavři jiný server a zkus znovu.")
        else:
            print(f"Chyba: {e}")
        input("Stiskni Enter pro ukončení...")
