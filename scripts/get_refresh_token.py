#!/usr/bin/env python3
"""Generate a Google Ads OAuth2 refresh token.

Usage:
    python scripts/get_refresh_token.py

Requires GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET
set as environment variables or in a .env file.
"""

import http.server
import os
import threading
import urllib.parse
import webbrowser

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import httpx
except ImportError:
    print("httpx non trovato, installa con: pip install httpx")
    raise SystemExit(1)

CLIENT_ID = os.environ.get("GOOGLE_ADS_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_ADS_CLIENT_SECRET", "")

if not CLIENT_ID:
    CLIENT_ID = input("Inserisci GOOGLE_ADS_CLIENT_ID: ").strip()
if not CLIENT_SECRET:
    CLIENT_SECRET = input("Inserisci GOOGLE_ADS_CLIENT_SECRET: ").strip()

REDIRECT_URI = "http://localhost:8085"
SCOPES = "https://www.googleapis.com/auth/adwords"

auth_code_result: dict[str, str] = {}


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)

        if "code" in params:
            auth_code_result["code"] = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h2>Autorizzazione completata!</h2>"
                b"<p>Puoi chiudere questa finestra.</p></body></html>"
            )
        else:
            error = params.get("error", ["unknown"])[0]
            auth_code_result["error"] = error
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                f"<html><body><h2>Errore: {error}</h2></body></html>".encode()
            )

    def log_message(self, format, *args):
        pass  # Suppress logs


def main():
    print("=" * 60)
    print("  Google Ads OAuth2 - Refresh Token Generator")
    print("=" * 60)
    print()

    # Build authorization URL
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode(
            {
                "client_id": CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "scope": SCOPES,
                "response_type": "code",
                "access_type": "offline",
                "prompt": "consent",
            }
        )
    )

    # Start local server
    server = http.server.HTTPServer(("localhost", 8085), CallbackHandler)
    server_thread = threading.Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    print("Apertura browser per autorizzazione Google...")
    print()
    print("Se il browser non si apre, visita manualmente:")
    print(auth_url)
    print()

    webbrowser.open(auth_url)
    server_thread.join(timeout=120)
    server.server_close()

    if "error" in auth_code_result:
        print(f"Errore durante l'autorizzazione: {auth_code_result['error']}")
        raise SystemExit(1)

    if "code" not in auth_code_result:
        print("Timeout: nessuna risposta ricevuta entro 2 minuti.")
        raise SystemExit(1)

    code = auth_code_result["code"]
    print("Codice autorizzazione ricevuto. Scambio per refresh token...")

    # Exchange code for tokens
    resp = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )

    if resp.status_code != 200:
        print(f"Errore scambio token: {resp.status_code}")
        print(resp.text)
        raise SystemExit(1)

    tokens = resp.json()
    refresh_token = tokens.get("refresh_token")

    if not refresh_token:
        print("Nessun refresh_token nella risposta:")
        print(tokens)
        raise SystemExit(1)

    print()
    print("=" * 60)
    print("  REFRESH TOKEN GENERATO CON SUCCESSO")
    print("=" * 60)
    print()
    print(f"  {refresh_token}")
    print()
    print("Aggiungilo alla configurazione MCP:")
    print(f'  "GOOGLE_ADS_REFRESH_TOKEN": "{refresh_token}"')
    print()


if __name__ == "__main__":
    main()
