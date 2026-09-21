#!/usr/bin/env python3
"""Mirror ARXOS release binaries to archive.org as a durable second home.

Designed to run in GitHub Actions (cloud to cloud): for every artifact that is
not yet mirrored, it downloads from the primary source (GitHub Releases for
kernels, Cloudflare R2 for ISOs), verifies the SHA-256 recorded in the manifest
(and computes it when the manifest does not have one yet), uploads the file to a
per-release archive.org item, then writes the resulting archive.org URL back
into the manifest. Idempotent: anything already carrying an archive_org URL is
skipped, so re-running only fills the gaps.

Credentials come from the environment (GitHub secrets), never the manifest:
    IA_ACCESS_KEY / IA_SECRET_KEY   archive.org S3 keys (account/s3.php)

Usage:
    mirror-to-archive.py --target all           # kernels + isos
    mirror-to-archive.py --target kernels
    mirror-to-archive.py --target isos --dry-run
    mirror-to-archive.py --target all --limit 1 # one release at a time
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, sys, tempfile, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
KERNELS = ROOT / "kernels.json"
ISOS = ROOT / "isos.json"
UA = "arxos-mirror/1.0 (+https://arxos.uk)"
CHUNK = 1 << 20  # 1 MiB


def log(*a): print(*a, flush=True)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(CHUNK), b""):
            h.update(b)
    return h.hexdigest()


def download(url: str, dest: pathlib.Path) -> None:
    log(f"    download {url}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        while True:
            b = r.read(CHUNK)
            if not b:
                break
            f.write(b); done += len(b)
        if total and done != total:
            raise IOError(f"short read: {done}/{total} bytes from {url}")


def source_base(urls: dict) -> str | None:
    """Where to pull the binary from: GitHub Releases first (stable, versioned),
    Cloudflare R2 as the fallback (and the only home for >2 GB ISOs)."""
    return urls.get("github") or urls.get("r2")


def ia_upload(identifier: str, files: dict[str, pathlib.Path], metadata: dict, dry: bool) -> str:
    """Upload one archive.org item. Returns the public download base URL."""
    url = f"https://archive.org/download/{identifier}/"
    if dry:
        log(f"    [dry-run] would upload item '{identifier}' with {list(files)}")
        return url
    from internetarchive import upload  # imported here so --dry-run needs no dep
    ak, sk = os.environ.get("IA_ACCESS_KEY"), os.environ.get("IA_SECRET_KEY")
    if not ak or not sk:
        sys.exit("IA_ACCESS_KEY / IA_SECRET_KEY are not set in the environment")
    responses = upload(
        identifier,
        files={name: str(p) for name, p in files.items()},
        metadata=metadata,
        access_key=ak, secret_key=sk,
        retries=5, retries_sleep=30, verbose=True,
    )
    for resp in responses:
        if resp.status_code not in (200, None):
            raise RuntimeError(f"archive.org upload failed ({resp.status_code}) for {identifier}")
    return url


def mirror_release(identifier: str, base: str, artifacts: dict, metadata: dict,
                   dry: bool, workdir: pathlib.Path) -> None:
    """Download every artifact for a release, verify/compute its SHA-256, and
    upload them together as one archive.org item. Files are removed after the
    upload so the runner disk never holds more than one release at a time."""
    if dry:
        for _role, art in artifacts.items():
            log(f"    [dry-run] would fetch {base.rstrip('/') + '/' + art['file']}")
        log(f"    [dry-run] would upload item '{identifier}' with {[a['file'] for a in artifacts.values()]}")
        return
    files: dict[str, pathlib.Path] = {}
    try:
        for _role, art in artifacts.items():
            fname = art["file"]
            dest = workdir / fname
            download(base.rstrip("/") + "/" + fname, dest)
            digest = sha256_file(dest)
            want = art.get("sha256")
            if want and want.lower() != digest.lower():
                raise ValueError(f"SHA-256 mismatch for {fname}: manifest {want} != downloaded {digest}")
            if not want:
                art["sha256"] = digest      # fill it in (e.g. the ISO)
                log(f"    computed sha256 {digest} for {fname}")
            if not art.get("size"):
                art["size"] = dest.stat().st_size
            files[fname] = dest
        ia_upload(identifier, files, metadata, dry)
    finally:
        for p in files.values():
            try: p.unlink()
            except OSError: pass


def kernel_metadata(k: dict) -> dict:
    return {
        "title": f"ArxOS kernel {k['flavor']} {k['version']}",
        "mediatype": "software",
        "creator": "Stingray Labs",
        "subject": ["ArxOS", "linux", "kernel", k["flavor"]],
        "date": k.get("date", ""),
        "description": (f"ArxOS prebuilt kernel {k['flavor']} {k['version']} "
                        f"(upstream {k.get('upstream','')}). Durable mirror of the "
                        f"ArxOS release binaries. Project: https://arxos.uk"),
        "licenseurl": "https://www.gnu.org/licenses/gpl-2.0.html",
    }


def iso_metadata(im: dict) -> dict:
    return {
        "title": im.get("title", f"ArxOS {im['version']}"),
        "mediatype": "software",
        "creator": "Stingray Labs",
        "subject": ["ArxOS", "linux", "iso", "operating system"],
        "date": im.get("date", ""),
        "description": (f"ArxOS {im['version']} ({im.get('edition','')}) installable "
                        f"ISO image. Durable mirror of the ArxOS release. "
                        f"Project: https://arxos.uk"),
        "licenseurl": "https://www.gnu.org/licenses/gpl-3.0.html",
    }


def process(manifest_path: pathlib.Path, key: str, id_for, meta_for, args, workdir) -> bool:
    if not manifest_path.exists():
        log(f"  {manifest_path.name}: not present, skipping")
        return False
    data = json.loads(manifest_path.read_text())
    changed = False
    done = 0
    for entry in data.get(key, []):
        urls = entry.setdefault("urls", {})
        if urls.get("archive_org"):
            continue  # already mirrored
        base = source_base(urls)
        if not base:
            log(f"  {id_for(entry)}: no source URL, skipping")
            continue
        if args.limit and done >= args.limit:
            log("  reached --limit, stopping"); break
        identifier = id_for(entry)
        log(f"  mirroring {identifier}  (source: {base})")
        mirror_release(identifier, base, entry.get("artifacts", {}),
                       meta_for(entry), args.dry_run, workdir)
        if not args.dry_run:
            urls["archive_org"] = f"https://archive.org/download/{identifier}/"
            entry["mirrored"] = __import__("datetime").date.today().isoformat()
            changed = True
        done += 1
    if changed:
        manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        log(f"  updated {manifest_path.name}")
    return changed


def kernel_id(k: dict) -> str:
    return f"arxos-{k['flavor']}-{k['version']}"


def iso_id(im: dict) -> str:
    return f"arxos-{im['version']}" + (f"-{im['edition']}" if im.get("edition") else "")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--target", choices=["all", "kernels", "isos"], default="all")
    p.add_argument("--dry-run", action="store_true", help="plan only, no download or upload")
    p.add_argument("--limit", type=int, default=0, help="mirror at most N releases this run (0 = no limit)")
    args = p.parse_args()

    changed = False
    with tempfile.TemporaryDirectory(prefix="arxos-mirror-") as td:
        workdir = pathlib.Path(td)
        if args.target in ("all", "kernels"):
            log("kernels.json:")
            changed |= process(KERNELS, "kernels", kernel_id, kernel_metadata, args, workdir)
        if args.target in ("all", "isos"):
            log("isos.json:")
            changed |= process(ISOS, "images", iso_id, iso_metadata, args, workdir)
    log("done." + (" manifest changed." if changed else " nothing to update."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
