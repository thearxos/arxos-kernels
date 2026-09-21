# arxos-mirror-cron

A Cloudflare Worker that triggers the archive.org mirror on a schedule.

On its cron (weekly by default), it calls the GitHub Actions `workflow_dispatch`
API to run [`mirror-archive.yml`](../.github/workflows/mirror-archive.yml) on
`thearxos/arxos-kernels`. **Cloudflare initiates; the GitHub runner executes** —
the runner is what downloads the multi-GB release binaries and uploads them to
archive.org, work a Worker's 128 MB / short-CPU budget cannot do. The mirror
script skips anything already mirrored without downloading, so a run with no new
release is a cheap no-op.

## Deploy

From this directory (`cron-worker/`), with the Cloudflare account that owns the
`thearxos` Workers:

```sh
# 1. GitHub token — a fine-grained PAT scoped to ONE repo:
#      Repository access: thearxos/arxos-kernels
#      Permissions: Actions -> Read and write
#    Create at https://github.com/settings/personal-access-tokens
#    Store it as a Worker secret (never in code or wrangler.jsonc):
wrangler secret put GH_TOKEN

# 2. (optional) a shared key to enable the manual POST /trigger test endpoint:
wrangler secret put TRIGGER_KEY

# 3. deploy
wrangler deploy
```

`wrangler deploy` registers the cron trigger automatically.

## Schedule

Edit `triggers.crons` in `wrangler.jsonc`:

- `"10 5 * * 0"` — weekly, Sundays 05:10 UTC (default)
- `"10 5 * * *"` — nightly, 05:10 UTC
- add more entries for multiple times

## Manual run (testing)

Only enabled when `TRIGGER_KEY` is set:

```sh
curl -X POST "https://arxos-mirror-cron.<your-subdomain>.workers.dev/trigger" \
  -H "x-trigger-key: <TRIGGER_KEY>"
# optional: ?target=kernels  |  ?target=isos  |  ?target=all (default)
```

A successful dispatch returns HTTP 202; the run then appears under the repo's
Actions tab. Check what the cron does at any time in the Cloudflare dashboard
(Workers > arxos-mirror-cron > Logs / Triggers).

## Security

- `GH_TOKEN` lives only as a Worker secret. Scope it to the single repo with
  Actions write and nothing else, so a leak cannot touch anything but this one
  workflow. Rotate it in GitHub and re-run `wrangler secret put GH_TOKEN` if needed.
- The `/trigger` endpoint is off unless `TRIGGER_KEY` is set, and rejects any
  request without the matching header.
