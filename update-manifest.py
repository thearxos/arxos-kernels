#!/usr/bin/env python3
"""Add or update a kernel entry in kernels.json, then (optionally) re-render the
README. Called by linux-arxos/kernel-publish.sh on a release; also runnable by hand.

    update-manifest.py --flavor linux-arxos --version 7.2.0-1 \
        --upstream "Linux 7.2.0" --date 2026-08 \
        --changes "..." \
        --kernel FILE --kernel-sha SHA --kernel-size N \
        --headers FILE --headers-sha SHA --headers-size N \
        --r2 https://.../kernels/ --github https://github.com/.../download/TAG/

The newly published version becomes `current`; the flavor's previous `current`
is demoted to `retired` and loses its R2 url (it moves to history-only)."""
import argparse, datetime, json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).parent
MF = HERE / "kernels.json"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--flavor", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--upstream", required=True)
    p.add_argument("--date", default=datetime.date.today().strftime("%Y-%m"))
    p.add_argument("--changes", required=True)
    p.add_argument("--kernel", required=True)
    p.add_argument("--kernel-sha", required=True)
    p.add_argument("--kernel-size", type=int, required=True)
    p.add_argument("--headers", required=True)
    p.add_argument("--headers-sha", required=True)
    p.add_argument("--headers-size", type=int, required=True)
    p.add_argument("--r2", default=None)
    p.add_argument("--github", required=True)
    p.add_argument("--no-readme", action="store_true")
    a = p.parse_args()

    m = json.loads(MF.read_text())
    m["updated"] = datetime.date.today().isoformat()
    m.setdefault("flavors", {}).setdefault(a.flavor, {"role": "", "base": "", "current": ""})
    m["flavors"][a.flavor]["current"] = a.version

    # demote the current entry(ies) of this flavor to retired, drop their R2 url
    for k in m.get("kernels", []):
        if k["flavor"] == a.flavor and k.get("status") == "current":
            k["status"] = "retired"
            k.setdefault("urls", {})["r2"] = None

    entry = {
        "flavor": a.flavor,
        "version": a.version,
        "upstream": a.upstream,
        "date": a.date,
        "status": "current",
        "changes": a.changes,
        "artifacts": {
            "kernel": {"file": a.kernel, "size": a.kernel_size, "sha256": a.kernel_sha},
            "headers": {"file": a.headers, "size": a.headers_size, "sha256": a.headers_sha},
        },
        "urls": {"r2": a.r2, "github": a.github, "archive_org": None},
    }
    # replace any existing same flavor+version, else prepend (newest first)
    kernels = [k for k in m.get("kernels", []) if not (k["flavor"] == a.flavor and k["version"] == a.version)]
    kernels.insert(0, entry)
    m["kernels"] = kernels

    MF.write_text(json.dumps(m, indent=2) + "\n")
    print(f"manifest: set {a.flavor} {a.version} as current")

    if not a.no_readme:
        subprocess.run([sys.executable, str(HERE / "gen-readme.py")], check=True)


if __name__ == "__main__":
    main()
