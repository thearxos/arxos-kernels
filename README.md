# arxos-kernels

The public history of every ARXOS **kernel** and **ISO image**. This repository
is text only: the kernel patch code and the build config stay private. What you
see here is the release history, the plain-English list of what each build adds,
the SHA-256 of every file, and where to download it. It also holds the automation
that mirrors every release to archive.org.

Binaries are hosted in more than one place so nothing ever disappears:

- **Cloudflare R2** — the current kernel and ISO, for fast downloads.
- **GitHub Releases** — every kernel version (ISOs are too large for Releases).
- **archive.org** — a durable mirror of every kernel and ISO, for the long haul.

_Manifests updated 2026-09-14._

## Kernels

| Flavor | Role | Base | Current |
| --- | --- | --- | --- |
| `linux-arxos` | default daily driver | Arch (ArxOS tuned) | 7.2.5-1 |
| `linux-arxos-rt` | real-time (RF, SDR, wireless capture) | Arch (ArxOS tuned) | 7.2.5-1 |

## What ARXOS adds

Every ARXOS kernel carries the same set of ARXOS additions on top of the base.
Each one is here for a reason, not for a spec sheet:

- **Live kernel patching.** Security and stability fixes can be applied to the running kernel without a reboot, so the machine stays up to date without downtime.
- **Kernel-level anonymity primitives.** The building blocks the ARXOS privacy tools rely on are compiled in: modern packet filtering, WireGuard, network and user isolation, and encrypted key storage. AnonKit and friends work at the kernel level, not bolted on top.
- **Low-level device access.** Fast, direct device input and output is enabled for the ARXOS device toolkit, including raw USB access and a high-performance I/O path. This is what lets droidB talk to hardware quickly and reliably.
- **Performance base.** ARXOS keeps a tuned performance profile: a responsive desktop scheduler, faster network throughput, a high timer rate, full preemption for low latency, a modern CPU baseline, and better memory behaviour under load. The result is a system that feels quick and stays quick.

## Kernel history

Newest first. Each entry says what changed against the kernel before it.

### linux-arxos-rt 7.2.5-1  (current)

- **Upstream base:** Linux 7.2.5
- **Released:** 2026-09
- **What changed:** Real-time (PREEMPT_RT + BORE) rebased onto Linux 7.2.5 with the full ARXOS hardening set: latest upstream security fixes, forced-threaded IRQs, RCU boost, 1000 Hz, plus lockdown, IMA, IOMMU-strict, init-on-alloc/free and live patching. No LTO (RT and LTO do not mix).
- **Kernel:** `linux-arxos-rt-7.2.5-1-x86_64.pkg.tar.zst` (154.1 MB, sha256 `d8c1898c86aa...`)
- **Headers:** `linux-arxos-rt-headers-7.2.5-1-x86_64.pkg.tar.zst` (43.8 MB, sha256 `028d94e7be6f...`)
- **Mirror:** archived on archive.org

### linux-arxos 7.2.5-1  (current)

- **Upstream base:** Linux 7.2.5
- **Released:** 2026-09
- **What changed:** Rebased onto Linux 7.2.5 with the full ARXOS performance and hardening set carried forward: latest upstream security fixes, tuned scheduler, full preemption, 1000 Hz, ThinLTO, plus lockdown, IMA, IOMMU-strict, init-on-alloc/free and live patching.
- **Kernel:** `linux-arxos-7.2.5-1-x86_64.pkg.tar.zst` (149.5 MB, sha256 `cb33dd21c5bd...`)
- **Headers:** `linux-arxos-headers-7.2.5-1-x86_64.pkg.tar.zst` (42.4 MB, sha256 `3126622fd8d5...`)

### linux-arxos-rt 7.2.0-2  (retired)

- **Upstream base:** Linux 7.2.0 (ArxOS realtime build)
- **Released:** 2026-09
- **What changed:** Real-time build (PREEMPT_RT) with the same 7.2.0-2 delta as the default flavor: DEATHSTROKE and hardening (memory wiped on free and alloc, hibernation disabled, IMA measured boot, IOMMU strict, kernel lockdown in integrity mode from early boot, restricted dmesg) plus live kernel patching. Bounded, predictable latency for RF, SDR, and wireless capture.
- **Kernel:** `linux-arxos-rt-7.2.0-2-x86_64.pkg.tar.zst` (154.2 MB, sha256 `4ef820317eae...`)
- **Headers:** `linux-arxos-rt-headers-7.2.0-2-x86_64.pkg.tar.zst` (43.8 MB, sha256 `be815470db79...`)

### linux-arxos 7.2.0-2  (retired)

- **Upstream base:** Linux 7.2.0 (ArxOS tuned)
- **Released:** 2026-09
- **What changed:** Adds the DEATHSTROKE and hardening delta: memory wiped on free and on alloc, hibernation disabled so no plaintext key lands in swap, IMA measured boot, IOMMU enforced in strict mode, kernel lockdown in integrity mode from early boot, restricted dmesg, and live kernel patching. Rebased on the latest 7.2.0 base with the full ArxOS tune set.
- **Kernel:** `linux-arxos-7.2.0-2-x86_64.pkg.tar.zst` (149.7 MB, sha256 `45bb7e593f20...`)
- **Headers:** `linux-arxos-headers-7.2.0-2-x86_64.pkg.tar.zst` (42.4 MB, sha256 `f4e7deac0d2d...`)

### linux-arxos-rt 7.2.0-1  (retired)

- **Upstream base:** Linux 7.2.0 (ArxOS realtime build)
- **Released:** 2026-08
- **What changed:** Real-time flavor: PREEMPT_RT + BORE. Same ArxOS tuning and the same offensive/defensive tool support as linux-arxos, but with hard real-time preemption (bounded worst-case latency, threaded IRQs) for RF, SDR, and wireless capture where timing must be exact. Trades a little raw throughput for predictable latency; linux-arxos stays the default daily driver.
- **Kernel:** `linux-arxos-rt-7.2.0-1-x86_64.pkg.tar.zst` (147.5 MB, sha256 `f6ce34664c0b...`)
- **Headers:** `linux-arxos-rt-headers-7.2.0-1-x86_64.pkg.tar.zst` (37.5 MB, sha256 `de8cc8546ccf...`)

### linux-arxos 7.2.0-1  (retired)

- **Upstream base:** Linux 7.2.0
- **Released:** 2026-08
- **What changed:** Rebased onto the newer upstream (Linux 7.2.0). Carries the full ARXOS tune set unchanged: live patching, kernel-level anonymity primitives, low-level device access, and the tuned performance base.
- **Kernel:** `linux-arxos-7.2.0-1-x86_64.pkg.tar.zst` (149.5 MB, sha256 `361410e6973e...`)
- **Headers:** `linux-arxos-headers-7.2.0-1-x86_64.pkg.tar.zst` (37.7 MB, sha256 `40b97f609efe...`)

### linux-arxos 7.1.3-1  (retired)

- **Upstream base:** Linux 7.1.3
- **Released:** 2026-07
- **What changed:** First kernel of this ARXOS line. Established the ARXOS tune set over the tuned base. Superseded by 7.2.0-1.
- **Kernel:** `linux-arxos-7.1.3-1-x86_64.pkg.tar.zst` (archived; hash restored when re-published)

## Images (ISOs)

| Edition | Version | Released | Status |
| --- | --- | --- | --- |
| `slim` | 0.0.1 | 2026-09 | current |

Newest first. ISOs live on R2 (primary) and archive.org (mirror); they are
too large for GitHub Releases.

### ArxOS 0.0.1 (slim)  (current)

- **Base:** Arch (ArxOS tuned)
- **Released:** 2026-09
- **What changed:** First public ArxOS release. Slim image: a lean base with the ArxOS toolkit built in; add the security arsenal on demand with arx after install. linux-arxos 7.2.5-1, zram baked in, DEATHSTROKE installed inert, install-gate verified on real hardware and in VMs.
- **Image:** `arxos-0.0.1.iso` (3.93 GB; sha256 recorded on the next mirror run)

## Getting a kernel

On ARXOS, use the Control Center Kernels panel, or the command line:

```
arxos-kernel list    linux-arxos      # every version, newest first
arxos-kernel latest  linux-arxos      # the newest version
arxos-kernel install linux-arxos      # install the latest
arxos-kernel install linux-arxos 7.1.3-1   # roll back to a specific version
```

The current kernel downloads from R2; older versions come from the full history.
Every download is checked against the sha256 in this manifest before it installs.

## Mirroring and automation

Every release is copied to archive.org as a durable second home, entirely in the
cloud — nothing depends on a maintainer's connection or upload speed.

- **`tools/mirror-to-archive.py`** downloads each release from its primary source
  (GitHub Releases for kernels, R2 for ISOs), verifies or computes the SHA-256,
  uploads it to a per-release archive.org item, and writes the archive.org URL
  back into the manifest. It is idempotent: anything already mirrored is skipped,
  so re-running only fills the gaps.
- **`.github/workflows/mirror-archive.yml`** runs that script on a GitHub runner
  (manual dispatch or on schedule) using the `IA_ACCESS_KEY` / `IA_SECRET_KEY`
  repository secrets.
- **`cron-worker/`** is a Cloudflare Worker that triggers the workflow on a cron,
  so the mirror stays in sync automatically. See `cron-worker/README.md`.

Publishing a new release updates the manifest, which the mirror then picks up:

- **Kernel:** `update-manifest.py` (run by the kernel publish step).
- **ISO:** upload the image to R2, then `update-isos.py --version X --file arxos-X.iso --changes "..."`.

A live, always-current view of every release is at
**<https://arxos.uk/releases.html>**.

