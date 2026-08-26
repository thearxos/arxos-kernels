#!/usr/bin/env python3
"""Generate README.md from kernels.json. Run after editing the manifest:
       python3 gen-readme.py
The manifest is the source of truth; the README is a rendered view of it."""
import json, pathlib

HERE = pathlib.Path(__file__).parent
M = json.loads((HERE / "kernels.json").read_text())


def mb(n):
    return "" if not n else f"{n / (1024 * 1024):.1f} MB"


def short(h):
    return "" if not h else h[:12]


lines = []
w = lines.append

w("# arxos-kernels")
w("")
w("The public history of every ARXOS kernel. This repository is text only. The")
w("kernel patch code and the build config stay private; what you see here is the")
w("release history, the plain-English list of what each kernel adds, and where to")
w("download it.")
w("")
w("Binaries are hosted twice so every kernel stays reachable:")
w("")
w("- **Cloudflare R2** holds the current kernel for fast downloads.")
w("- **GitHub Releases and archive.org** hold the full history for rollback.")
w("")
w(f"_Manifest updated {M['updated']}._")
w("")

# flavors / current
w("## Kernels")
w("")
w("| Flavor | Role | Base | Current |")
w("| --- | --- | --- | --- |")
for name, f in M["flavors"].items():
    w(f"| `{name}` | {f['role']} | {f['base']} | {f['current']} |")
w("")

# what ARXOS adds
w("## What ARXOS adds")
w("")
w("Every ARXOS kernel carries the same set of ARXOS additions on top of the base.")
w("Each one is here for a reason, not for a spec sheet:")
w("")
for t in M["tunes"]:
    w(f"- **{t['name']}.** {t['advantage']}")
w("")

# history
w("## History")
w("")
w("Newest first. Each entry says what changed against the kernel before it.")
w("")
for k in M["kernels"]:
    tag = "current" if k["status"] == "current" else k["status"]
    w(f"### {k['flavor']} {k['version']}  ({tag})")
    w("")
    w(f"- **Upstream base:** {k['upstream']}")
    w(f"- **Released:** {k['date']}")
    w(f"- **What changed:** {k['changes']}")
    art = k["artifacts"]
    kern, hdr = art["kernel"], art["headers"]
    if kern.get("sha256"):
        w(f"- **Kernel:** `{kern['file']}` ({mb(kern['size'])}, sha256 `{short(kern['sha256'])}...`)")
        w(f"- **Headers:** `{hdr['file']}` ({mb(hdr['size'])}, sha256 `{short(hdr['sha256'])}...`)")
    else:
        w(f"- **Kernel:** `{kern['file']}` (archived; hash restored when re-published)")
    w("")

# how to get
w("## Getting a kernel")
w("")
w("On ARXOS, use the Control Center Kernels panel, or the command line:")
w("")
w("```")
w("arxos-kernel list    linux-arxos      # every version, newest first")
w("arxos-kernel latest  linux-arxos      # the newest version")
w("arxos-kernel install linux-arxos      # install the latest")
w("arxos-kernel install linux-arxos 7.1.3-1   # roll back to a specific version")
w("```")
w("")
w("The current kernel downloads from R2; older versions come from the full history.")
w("Every download is checked against the sha256 in this manifest before it installs.")
w("")

(HERE / "README.md").write_text("\n".join(lines) + "\n")
print("wrote README.md")
