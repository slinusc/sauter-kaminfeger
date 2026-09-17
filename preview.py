#!/usr/bin/env python3
"""Baut eine Kunden-Vorschau fuer GitHub Pages.

GitHub Pages liefert ein Projekt unter https://<user>.github.io/<repo>/ aus,
also in einem Unterordner. Die Seiten verwenden absolute Pfade (/assets/...,
/team/), die dort ins Leere zeigen. Dieses Skript baut dist/ neu und kopiert
es in einen Zielordner, wobei alle internen Pfade relativ gemacht werden.

Zusaetzlich ist die Vorschau fuer Suchmaschinen gesperrt (noindex +
robots.txt), damit sie nicht als Duplikat der spaeteren Live-Seite rankt.
Live-Dateien (_redirects, sitemap.xml) fehlen bewusst.

Wird auf GitHub von .github/workflows/preview.yml bei jedem Push ausgefuehrt.

Aufruf:  python3 preview.py [Zielordner]   (Standard _site)
"""
import os
import re
import shutil
import sys

import publish

TARGET = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else
                         os.path.join(publish.ROOT, "_site"))
SKIP = {"_redirects", "sitemap.xml", "robots.txt"}

ATTR = re.compile(r'\b(href|src|poster)="/(?!/)([^"]*)"')
SRCSET = re.compile(r'\bsrcset="([^"]*)"')
ROBOTS_META = re.compile(r'<meta name="robots" content="[^"]*">')
NOINDEX = '<meta name="robots" content="noindex,nofollow">'


def relative(html, prefix):
    html = ATTR.sub(lambda m: f'{m.group(1)}="{prefix}{m.group(2)}"', html)
    html = SRCSET.sub(lambda m: 'srcset="' + re.sub(r'(^|,\s*)/(?!/)', lambda n: n.group(1) + prefix, m.group(1)) + '"', html)
    return html


def main():
    publish.main()

    os.makedirs(TARGET, exist_ok=True)
    for name in os.listdir(TARGET):
        if name == ".git":
            continue
        p = os.path.join(TARGET, name)
        shutil.rmtree(p) if os.path.isdir(p) and not os.path.islink(p) else os.remove(p)

    shutil.copytree(publish.DIST, TARGET, dirs_exist_ok=True,
                    ignore=lambda d, names: [n for n in names if d == publish.DIST and n in SKIP])

    pages = 0
    for dirpath, _, files in os.walk(TARGET):
        if ".git" in dirpath.split(os.sep):
            continue
        for f in files:
            path = os.path.join(dirpath, f)
            if f == "index.html":
                depth = len(os.path.relpath(dirpath, TARGET).split(os.sep)) if dirpath != TARGET else 0
                html = open(path, encoding="utf-8").read()
                html = relative(html, "../" * depth or "./")
                if ROBOTS_META.search(html):
                    html = ROBOTS_META.sub(NOINDEX, html)
                else:
                    html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + NOINDEX, 1)
                open(path, "w", encoding="utf-8").write(html)
                pages += 1
            elif f == "site.css":
                css = open(path, encoding="utf-8").read()
                open(path, "w", encoding="utf-8").write(re.sub(r"url\((['\"]?)/(?!/)", r"url(\1", css))

    for name, content in {
        "robots.txt": "User-agent: *\nDisallow: /\n",
        ".nojekyll": "",
    }.items():
        with open(os.path.join(TARGET, name), "w", encoding="utf-8") as fh:
            fh.write(content)

    print(f"\nVorschau fertig – {pages} Seiten mit relativen Pfaden -> {TARGET}")


if __name__ == "__main__":
    main()
