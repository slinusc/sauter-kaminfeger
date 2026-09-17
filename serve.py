#!/usr/bin/env python3
"""Entwicklungsserver mit echten URLs – ohne Build-Schritt.

Serviert den Projektordner, bildet aber die sauberen URLs direkt auf die
Artboards ab:

    /                      ->  Sauter Landingpage.dc.html
    /komfortlueftung/      ->  Komfortlueftung.dc.html
    /assets/... , /site.css, /support.js   ->  wie gehabt

Damit lassen sich die .dc.html-Dateien bearbeiten und sofort neu laden;
publish.py wird nur fuer das Deployment gebraucht.

Aufruf:  python3 serve.py [Port]        (Standard 8000)
"""
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote, urlparse

from publish import ALIASES, ROUTES

HERE = os.path.dirname(os.path.abspath(__file__))

# "" / "komfortlueftung" / ... -> Artboard-Dateiname
URL2FILE = {route: artboard for artboard, route in ROUTES.items()}
URL2FILE.update(ALIASES)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def translate_path(self, path):
        route = unquote(urlparse(path).path).strip("/")
        if route in URL2FILE:
            return os.path.join(HERE, URL2FILE[route])
        return super().translate_path(path)

    def end_headers(self):
        # Im Dev-Betrieb nie cachen, damit Aenderungen sofort sichtbar sind.
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        code = str(args[1]) if len(args) > 1 else "?"
        if code.startswith(("4", "5")):
            sys.stderr.write(f"  {code}  {args[0]}\n")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Sauter-Dev-Server auf http://localhost:{port}/")
    print(f"{len(URL2FILE)} Routen – Strg+C zum Beenden\n")
    for route in sorted(URL2FILE):
        print(f"  http://localhost:{port}/{route}{'/' if route else ''}")
    print()
    try:
        HTTPServer(("", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nbeendet")


if __name__ == "__main__":
    main()
