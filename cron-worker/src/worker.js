/**
 * arxos-mirror-cron — Cloudflare Worker
 *
 * A tiny cron trigger for the archive.org mirror. On its schedule it calls the
 * GitHub Actions workflow_dispatch API to run `mirror-archive.yml` on
 * thearxos/arxos-kernels. Cloudflare *initiates*; the GitHub runner does the
 * heavy lifting (downloading multi-GB release binaries and pushing them to
 * archive.org), which a Worker's memory and time budget cannot do itself.
 *
 * The mirror script is idempotent: releases that already carry an archive_org
 * URL are skipped without downloading, so a run with nothing new is a cheap
 * no-op. That makes a periodic schedule safe as a backup safety net.
 *
 * Secrets (set with `wrangler secret put <NAME>`, never in code or config):
 *   GH_TOKEN     GitHub fine-grained PAT, repo thearxos/arxos-kernels,
 *                permission "Actions: read and write". Required.
 *   TRIGGER_KEY  optional shared key that enables manual POST /trigger runs.
 *
 * Optional vars (wrangler.jsonc [vars], all have sane defaults):
 *   REPO (thearxos/arxos-kernels), WORKFLOW (mirror-archive.yml),
 *   REF (main), TARGET (all)
 */

const GH_API = "https://api.github.com";

async function dispatchMirror(env, target) {
  if (!env.GH_TOKEN) {
    return { ok: false, status: 0, detail: "GH_TOKEN secret is not set" };
  }
  const repo = env.REPO || "thearxos/arxos-kernels";
  const workflow = env.WORKFLOW || "mirror-archive.yml";
  const ref = env.REF || "main";
  const url = `${GH_API}/repos/${repo}/actions/workflows/${workflow}/dispatches`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.GH_TOKEN}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "arxos-mirror-cron",
      "Content-Type": "application/json",
    },
    // Only pass `target`; dry_run and limit use their workflow defaults.
    body: JSON.stringify({ ref, inputs: { target: target || env.TARGET || "all" } }),
  });
  // A successful workflow_dispatch returns 204 No Content.
  const ok = res.status === 204;
  return { ok, status: res.status, detail: ok ? "workflow dispatched" : await res.text() };
}

export default {
  // Cron Trigger — schedule lives in wrangler.jsonc [triggers.crons].
  async scheduled(event, env, ctx) {
    ctx.waitUntil(
      dispatchMirror(env).then((r) => {
        console.log(`[cron ${event.cron}] mirror dispatch: ${r.status} ${r.detail}`);
      })
    );
  },

  // Manual trigger for testing: POST /trigger with header `x-trigger-key: <TRIGGER_KEY>`.
  // Optional ?target=kernels|isos|all. Disabled unless TRIGGER_KEY is set.
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/trigger") {
      if (request.method !== "POST") {
        return json({ error: "use POST" }, 405);
      }
      if (!env.TRIGGER_KEY || request.headers.get("x-trigger-key") !== env.TRIGGER_KEY) {
        return json({ error: "forbidden" }, 403);
      }
      const target = url.searchParams.get("target") || undefined;
      const r = await dispatchMirror(env, target);
      return json(r, r.ok ? 202 : 502);
    }
    return new Response(
      "arxos-mirror-cron: runs the archive.org mirror on a schedule.\n" +
        "POST /trigger (with x-trigger-key) to run it manually.\n",
      { status: 200, headers: { "content-type": "text/plain; charset=utf-8" } }
    );
  },
};

function json(obj, status) {
  return new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}
