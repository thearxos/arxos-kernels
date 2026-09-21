#!/usr/bin/env python3
"""Add or update an ISO entry in isos.json — the image analog of
update-manifest.py. Run it once per new ISO, after uploading the image to R2;
the archive.org mirror (mirror-to-archive.py) then computes the SHA-256 and
records the archive.org URL on its next run, and the release page shows it.

    update-isos.py --version 0.0.2 --edition slim --date 2026-10 \
        --file arxos-0.0.2.iso \
        --changes "What changed in this image." \
        [--r2 https://pub-XXXX.r2.dev/]   # default: the current ArxOS R2 base
        [--size N]                         # default: HEAD the R2 object
        [--sha SHA256]                     # default: left blank; the mirror fills it
        [--upstream "Arch (ArxOS tuned)"] [--title "ArxOS 0.0.2 (slim)"]

The new version becomes `current`; any previous `current` of the SAME edition is
demoted to `retired` (its download URLs are kept, so old images stay reachable —
manage R2 retention separately if you want to free space). Binaries are never
touched: you upload the ISO to R2 once, this only edits the manifest.
"""
import argparse, datetime, json, pathlib, sys, urllib.request

HERE = pathlib.Path(__file__).parent
MF = HERE / "isos.json"
DEFAULT_R2 = "https://pub-d5ff3efb1d204998aa120ded02d070b9.r2.dev/"


def head_size(base, file):
    """Best-effort Content-Length of the R2 object, or None."""
    url = base.rstrip("/") + "/" + file
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "update-isos/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            n = r.headers.get("Content-Length")
            return int(n) if n else None
    except Exception as e:
        print(f"  note: could not HEAD {url} for size ({e}); leaving size null", file=sys.stderr)
        return None


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", required=True)
    p.add_argument("--edition", default="slim")
    p.add_argument("--file", required=True, help="ISO filename, e.g. arxos-0.0.2.iso")
    p.add_argument("--changes", required=True)
    p.add_argument("--date", default=datetime.date.today().strftime("%Y-%m"))
    p.add_argument("--upstream", default="Arch (ArxOS tuned)")
    p.add_argument("--title", default=None, help="default: 'ArxOS <version> (<edition>)'")
    p.add_argument("--r2", default=DEFAULT_R2, help="R2 base URL the ISO lives under")
    p.add_argument("--size", type=int, default=None, help="bytes; default HEADs the R2 object")
    p.add_argument("--sha", default=None, help="SHA-256; default blank, the mirror computes it")
    a = p.parse_args()

    if not MF.exists():
        sys.exit(f"{MF} not found (run from the arxos-kernels repo root)")
    m = json.loads(MF.read_text())
    m["updated"] = datetime.date.today().isoformat()
    m.setdefault("images", [])

    # demote the previous current image(s) of this edition to retired
    for im in m["images"]:
        if im.get("edition") == a.edition and im.get("status") == "current":
            im["status"] = "retired"

    size = a.size if a.size is not None else head_size(a.r2, a.file)
    title = a.title or f"ArxOS {a.version}" + (f" ({a.edition})" if a.edition else "")

    entry = {
        "edition": a.edition,
        "version": a.version,
        "title": title,
        "upstream": a.upstream,
        "date": a.date,
        "status": "current",
        "changes": a.changes,
        "artifacts": {
            "iso": {"file": a.file, "size": size, "sha256": a.sha},
        },
        "urls": {"r2": a.r2, "github": None, "archive_org": None},
    }
    # replace any existing same edition+version, else prepend (newest first)
    images = [im for im in m["images"] if not (im.get("edition") == a.edition and im.get("version") == a.version)]
    images.insert(0, entry)
    m["images"] = images

    MF.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    print(f"isos.json: set {a.edition} {a.version} as current"
          + (f" (size {size} bytes)" if size else " (size unknown; mirror will fill it)"))


if __name__ == "__main__":
    main()
