#!/usr/bin/env python3
"""Baut die auslieferbare Website nach dist/.

Die .dc.html-Artboards behalten ihre Namen, damit der Canvas-Editor damit
arbeiten kann. Dieses Skript bildet sie auf saubere URLs ab:

    Sauter Landingpage.dc.html  ->  dist/index.html
    Komfortlueftung.dc.html     ->  dist/komfortlueftung/index.html

Aufruf:  python3 publish.py && (cd dist && python3 -m http.server 8080)
"""
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")

# Artboard -> URL-Pfad ("" = Startseite)
ROUTES = {
    "Sauter Landingpage.dc.html":   "",
    "Kaminfegerarbeiten.dc.html":   "kaminfegerarbeiten",
    "Oelheizungen.dc.html":         "oelheizungen",
    "Holzheizung.dc.html":          "holzheizung",
    "Gasheizungen.dc.html":         "gasheizungen",
    "Kacheloefen Cheminee.dc.html": "kachelofen-cheminee",
    "Feuerungskontrolle.dc.html":   "feuerungskontrolle",
    "Neutrale Beratung.dc.html":    "neutrale-beratung",
    "Lueftungsreinigung.dc.html":   "lueftungsreinigung",
    "Bad WC Abluftanlagen.dc.html": "bad-wc-abluftanlagen",
    "Komfortlueftung.dc.html":      "komfortlueftung",
    "Videoinspektion.dc.html":      "videoinspektion",
    "Tiefgaragenlueftung.dc.html":  "tiefgaragenlueftung",
    "CO2 Messungen.dc.html":        "co2-messung",
    "Serviceplan.dc.html":          "serviceplan",
    "Team.dc.html":                 "team",
    "Kontakt.dc.html":              "kontakt",
    "Impressum.dc.html":            "impressum",
}

# Zusätzliche URLs, die dieselbe Seite ausliefern
ALIASES = {"datenschutz": "Impressum.dc.html"}

STATIC_DIRS = ["assets"]
STATIC_FILES = ["support.js", "site.css", "nav.js", "robots.txt", "sitemap.xml", "_redirects"]


def emit(artboard, route):
    src = os.path.join(ROOT, artboard)
    if not os.path.exists(src):
        raise SystemExit(f"fehlt: {artboard}")
    out_dir = os.path.join(DIST, route) if route else DIST
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "index.html"))
    return f"/{route}/" if route else "/"


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    for artboard, route in ROUTES.items():
        print(f"  {emit(artboard, route):26s} <- {artboard}")
    for route, artboard in ALIASES.items():
        print(f"  {emit(artboard, route):26s} <- {artboard}  (Alias)")

    for d in STATIC_DIRS:
        s = os.path.join(ROOT, d)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(DIST, d))
            print(f"  kopiert: {d}/")
    for f in STATIC_FILES:
        s = os.path.join(ROOT, f)
        if os.path.exists(s):
            shutil.copyfile(s, os.path.join(DIST, f))
            print(f"  kopiert: {f}")

    # _masters/ wird bewusst NICHT ausgeliefert.
    total = sum(os.path.getsize(os.path.join(dp, f))
                for dp, _, fs in os.walk(DIST) for f in fs)
    print(f"\ndist/ fertig – {len(ROUTES) + len(ALIASES)} URLs, {total / 1048576:.1f} MB")


if __name__ == "__main__":
    main()
