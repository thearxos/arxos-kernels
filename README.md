# arxos-kernels

The public history of every ARXOS kernel. This repository is text only. The
kernel patch code and the build config stay private; what you see here is the
release history, the plain-English list of what each kernel adds, and where to
download it.

Binaries are hosted twice so every kernel stays reachable:

- **Cloudflare R2** holds the current kernel for fast downloads.
- **GitHub Releases and archive.org** hold the full history for rollback.

_Manifest updated 2026-08-27._

## Kernels

| Flavor | Role | Base | Current |
| --- | --- | --- | --- |
| `linux-arxos` | default daily driver | Arch (ArxOS tuned) | 7.2.0-1 |
| `linux-arxos-rt` | real-time (RF, SDR, wireless capture) | Arch (ArxOS tuned) | 7.2.0-1 |

## What ARXOS adds

Every ARXOS kernel carries the same set of ARXOS additions on top of the base.
Each one is here for a reason, not for a spec sheet:

- **Live kernel patching.** Security and stability fixes can be applied to the running kernel without a reboot, so the machine stays up to date without downtime.
- **Kernel-level anonymity primitives.** The building blocks the ARXOS privacy tools rely on are compiled in: modern packet filtering, WireGuard, network and user isolation, and encrypted key storage. AnonKit and friends work at the kernel level, not bolted on top.
- **Low-level device access.** Fast, direct device input and output is enabled for the ARXOS device toolkit, including raw USB access and a high-performance I/O path. This is what lets droidB talk to hardware quickly and reliably.
- **Performance base.** ARXOS keeps a tuned performance profile: a responsive desktop scheduler, faster network throughput, a high timer rate, full preemption for low latency, a modern CPU baseline, and better memory behaviour under load. The result is a system that feels quick and stays quick.

## History

Newest first. Each entry says what changed against the kernel before it.

### linux-arxos-rt 7.2.0-1  (current)

- **Upstream base:** Linux 7.2.0 (ArxOS realtime build)
- **Released:** 2026-08
- **What changed:** Real-time flavor: PREEMPT_RT + BORE. Same ArxOS tuning and the same offensive/defensive tool support as linux-arxos, but with hard real-time preemption (bounded worst-case latency, threaded IRQs) for RF, SDR, and wireless capture where timing must be exact. Trades a little raw throughput for predictable latency; linux-arxos stays the default daily driver.
- **Kernel:** `linux-arxos-rt-7.2.0-1-x86_64.pkg.tar.zst` (147.5 MB, sha256 `f6ce34664c0b...`)
- **Headers:** `linux-arxos-rt-headers-7.2.0-1-x86_64.pkg.tar.zst` (37.5 MB, sha256 `de8cc8546ccf...`)

### linux-arxos 7.2.0-1  (current)

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


---

<div align="center">
<sub><b>arxos-kernels</b> is part of the <b>ArxOS</b> project, built by <b>Stingray Labs</b>.</sub>
</div>
