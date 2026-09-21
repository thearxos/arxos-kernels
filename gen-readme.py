#!/usr/bin/env python3
"""Generate README.md from kernels.json and isos.json. Run after editing a
manifest:
       python3 gen-readme.py
The manifests are the source of truth; the README is a rendered view of them."""
import json, pathlib

HERE = pathlib.Path(__file__).parent
M = json.loads((HERE / "kernels.json").read_text())
ISO_PATH = HERE / "isos.json"
I = json.loads(ISO_PATH.read_text()) if ISO_PATH.exists() else {"images": []}


def mb(n):
    return "" if not n else f"{n / (1024 * 1024):.1f} MB"


def gb(n):
    return "" if not n else f"{n / (1024 ** 3):.2f} GB"


def short(h):
    return "" if not h else h[:12]


lines = []
w = lines.append

w("# arxos-kernels")
w("")
w("The public history of every ARXOS **kernel** and **ISO image**. This repository")
w("is text only: the kernel patch code and the build config stay private. What you")
w("see here is the release history, the plain-English list of what each build adds,")
w("the SHA-256 of every file, and where to download it. It also holds the automation")
w("that mirrors every release to archive.org.")
w("")
w("Binaries are hosted in more than one place so nothing ever disappears:")
w("")
w("- **Cloudflare R2** — the current kernel and ISO, for fast downloads.")
w("- **GitHub Releases** — every kernel version (ISOs are too large for Releases).")
w("- **archive.org** — a durable mirror of every kernel and ISO, for the long haul.")
w("")
w(f"_Manifests updated {M['updated']}._")
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

# kernel history
w("## Kernel history")
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
    if k.get("urls", {}).get("archive_org"):
        w(f"- **Mirror:** archived on archive.org")
    w("")

# ISO images
w("## Images (ISOs)")
w("")
if I.get("images"):
    w("| Edition | Version | Released | Status |")
    w("| --- | --- | --- | --- |")
    for im in I["images"]:
        w(f"| `{im.get('edition','')}` | {im['version']} | {im.get('date','')} | {im.get('status','')} |")
    w("")
    w("Newest first. ISOs live on R2 (primary) and archive.org (mirror); they are")
    w("too large for GitHub Releases.")
    w("")
    for im in I["images"]:
        tag = im.get("status", "")
        title = f"ArxOS {im['version']}" + (f" ({im['edition']})" if im.get("edition") else "")
        w(f"### {title}  ({tag})")
        w("")
        w(f"- **Base:** {im.get('upstream','')}")
        w(f"- **Released:** {im.get('date','')}")
        w(f"- **What changed:** {im.get('changes','')}")
        iso = im["artifacts"]["iso"]
        if iso.get("sha256"):
            w(f"- **Image:** `{iso['file']}` ({gb(iso['size'])}, sha256 `{short(iso['sha256'])}...`)")
        else:
            w(f"- **Image:** `{iso['file']}` ({gb(iso['size'])}; sha256 recorded on the next mirror run)")
        if im.get("urls", {}).get("archive_org"):
            w(f"- **Mirror:** archived on archive.org")
        w("")
else:
    w("_No ISO images tracked yet._")
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

# mirroring / automation
w("## Mirroring and automation")
w("")
w("Every release is copied to archive.org as a durable second home, entirely in the")
w("cloud — nothing depends on a maintainer's connection or upload speed.")
w("")
w("- **`tools/mirror-to-archive.py`** downloads each release from its primary source")
w("  (GitHub Releases for kernels, R2 for ISOs), verifies or computes the SHA-256,")
w("  uploads it to a per-release archive.org item, and writes the archive.org URL")
w("  back into the manifest. It is idempotent: anything already mirrored is skipped,")
w("  so re-running only fills the gaps.")
w("- **`.github/workflows/mirror-archive.yml`** runs that script on a GitHub runner")
w("  (manual dispatch or on schedule) using the `IA_ACCESS_KEY` / `IA_SECRET_KEY`")
w("  repository secrets.")
w("- **`cron-worker/`** is a Cloudflare Worker that triggers the workflow on a cron,")
w("  so the mirror stays in sync automatically. See `cron-worker/README.md`.")
w("")
w("Publishing a new release updates the manifest, which the mirror then picks up:")
w("")
w("- **Kernel:** `update-manifest.py` (run by the kernel publish step).")
w('- **ISO:** upload the image to R2, then `update-isos.py --version X --file'
  ' arxos-X.iso --changes "..."`.')
w("")
w("A live, always-current view of every release is at")
w("**<https://arxos.uk/releases.html>**.")
w("")

(HERE / "README.md").write_text("\n".join(lines) + "\n")
print("wrote README.md")
