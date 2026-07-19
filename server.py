"""
Docházka Agent — lokální proxy server
Spouští se přes spustit_agenta.bat nebo spustit_agenta.sh
"""

import http.server
import json
import socket
import urllib.request
import urllib.error
import base64
import os
import sys
import webbrowser
import threading

PORT = 8080
HTML_FILE = "dochazka_agent.html"
JIRA_HOST = "packeta.atlassian.net"

# ── DNS záchranná síť ─────────────────────────────────────────────────────────
# Na některých Windows selhává getaddrinfo uvnitř HTTP handleru, i když jinak
# funguje. Při startu si IP adresu zapamatujeme a při selhání DNS ji použijeme.
CACHED_IP = None
_orig_getaddrinfo = socket.getaddrinfo

def _patched_getaddrinfo(host, *args, **kwargs):
    try:
        return _orig_getaddrinfo(host, *args, **kwargs)
    except socket.gaierror as e:
        print(f"[DNS selhalo] host={host!r} chyba={e}")
        if str(host) == JIRA_HOST and CACHED_IP:
            print(f"[DNS fallback] Používám cached IP {CACHED_IP} pro {JIRA_HOST}")
            return _orig_getaddrinfo(CACHED_IP, *args, **kwargs)
        raise

socket.getaddrinfo = _patched_getaddrinfo

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
            jira_path = self.path[5:]  # odstraň /jira (ponech lomítko)
            auth = self.headers.get("X-Jira-Auth", "")
            self._proxy_jira("GET", jira_path, auth)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        # Proxy POST requesty na Jira
        if self.path.startswith("/jira/"):
            jira_path = self.path[5:]
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
            "User-Agent": "DochazkaAgent/1.0",
        }
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        # Zkus nejdřív přímé spojení (bez systémového proxy),
        # pak se systémovým proxy — jeden z nich by měl fungovat
        openers = [
            urllib.request.build_opener(urllib.request.ProxyHandler({})),   # bez proxy
            urllib.request.build_opener(),                                   # se systémovým proxy
        ]

        last_error = None
        for opener in openers:
            try:
                with opener.open(req, timeout=30) as resp:
                    data = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", "application/json")
                    self.send_cors_headers()
                    self.end_headers()
                    self.wfile.write(data)
                    return
            except urllib.error.HTTPError as e:
                # HTTP chyba (401, 404...) = spojení funguje, jen Jira vrátila chybu
                data = e.read()
                self.send_response(e.code)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception as e:
                last_error = e
                print(f"[Proxy chyba] {type(e).__name__}: {e}")
                continue  # zkus další opener

        # Oba openery selhaly
        self.send_response(500)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": str(last_error),
            "hint": "Server se nemohl připojit k packeta.atlassian.net. Zkontroluj internet/VPN/firewall."
        }).encode())


def open_browser():
    import time
    time.sleep(1)
    webbrowser.open(f"http://localhost:{PORT}/{HTML_FILE}")


def startup_diagnostics():
    """Otestuj DNS a připojení k Jiře hned při startu."""
    print("--- Diagnostika ---")
    print(f"Python: {sys.executable}")
    print(f"Proxy env: HTTP_PROXY={os.environ.get('HTTP_PROXY', os.environ.get('http_proxy', '-'))}, HTTPS_PROXY={os.environ.get('HTTPS_PROXY', os.environ.get('https_proxy', '-'))}")
    try:
        print(f"Systémové proxy (registr/OS): {urllib.request.getproxies()}")
    except Exception as e:
        print(f"getproxies() selhalo: {e}")
    global CACHED_IP
    try:
        ip = socket.gethostbyname(JIRA_HOST)
        CACHED_IP = ip
        print(f"DNS OK: {JIRA_HOST} -> {ip} (uloženo pro fallback)")
    except Exception as e:
        print(f"DNS SELHALO: {e}")
    try:
        req = urllib.request.Request("https://packeta.atlassian.net/status", headers={"User-Agent": "DochazkaAgent/1.0"})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=10) as r:
            print(f"Spojení s Jirou OK (HTTP {r.status})")
    except urllib.error.HTTPError as e:
        print(f"Spojení s Jirou OK (HTTP {e.code})")
    except Exception as e:
        print(f"Spojení s Jirou SELHALO: {e}")
    print("-------------------\n")


if __name__ == "__main__":
    # Zkontroluj že HTML soubor existuje
    if not os.path.exists(HTML_FILE):
        print(f"CHYBA: {HTML_FILE} nenalezen ve stejné složce jako server.py")
        input("Stiskni Enter pro ukončení...")
        sys.exit(1)

    startup_diagnostics()

    print(f"Docházka Agent běží na http://localhost:{PORT}/{HTML_FILE}")
    print("Zavři toto okno až skončíš.\n")

    # Otevři prohlížeč po 1 sekundě
    threading.Thread(target=open_browser, daemon=True).start()

    try:
        server = http.server.ThreadingHTTPServer(("", PORT), ProxyHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer zastaven.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {PORT} je již obsazen. Zavři jiný server a zkus znovu.")
        else:
            print(f"Chyba: {e}")
        input("Stiskni Enter pro ukončení...")
