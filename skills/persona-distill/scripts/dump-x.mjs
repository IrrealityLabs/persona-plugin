#!/usr/bin/env node
// Dump X (Twitter) posts for persona distillation.
//
// Usage:
//   node dump-x.mjs --slug=<slug> --user=<handle> [--user=<handle> ...] [--max=1000] [--include-replies]
//
// Reads X_BEARER_TOKEN from process.env or ./.env in the cwd.
// Writes to <store>/assets/<slug>/x-posts.jsonl and x-metadata.json,
// where <store> is $PERSONA_HOME if set, else ./.personas in the cwd.
//
// Requires Node 18+ (built-in fetch). No npm install needed.
// X API: requires at least Basic tier ($200/mo as of 2026) for read access.

import { readFileSync, existsSync, mkdirSync, createWriteStream } from 'node:fs';
import { writeFile } from 'node:fs/promises';
import { join, resolve } from 'node:path';

// ---------- arg parsing ----------

function parseArgs(argv) {
  const out = { users: [], max: 1000, includeReplies: false };
  for (const arg of argv) {
    if (arg.startsWith('--slug=')) out.slug = arg.slice(7);
    else if (arg.startsWith('--user=')) out.users.push(arg.slice(7).replace(/^@/, ''));
    else if (arg.startsWith('--max=')) out.max = Number(arg.slice(6));
    else if (arg === '--include-replies') out.includeReplies = true;
    else if (!arg.startsWith('--')) {
      if (!out.slug) out.slug = arg;
    }
  }
  if (!out.slug) die('missing --slug=<persona-slug>');
  if (out.users.length === 0) die('need at least one --user=<handle>');
  if (!Number.isFinite(out.max) || out.max <= 0) die(`invalid --max: ${out.max}`);
  return out;
}

function die(msg) {
  console.error(`error: ${msg}`);
  console.error('usage: node dump-x.mjs --slug=<slug> --user=<handle> [--user=<handle> ...] [--max=1000] [--include-replies]');
  process.exit(1);
}

// ---------- .env loader (minimal) ----------

function loadEnv() {
  const envPath = resolve(process.cwd(), '.env');
  if (!existsSync(envPath)) return;
  const text = readFileSync(envPath, 'utf8');
  for (const line of text.split('\n')) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/i);
    if (!m) continue;
    let val = m[2];
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    if (!process.env[m[1]]) process.env[m[1]] = val;
  }
}

// ---------- X API client ----------

const X_BASE = 'https://api.x.com/2';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function xget(token, path, params = {}) {
  const url = new URL(`${X_BASE}${path}`);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
  }
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (res.status === 429) {
    const reset = Number(res.headers.get('x-rate-limit-reset')) * 1000;
    const wait = Math.max(0, reset - Date.now()) + 1000;
    console.error(`rate limited; sleeping ${Math.round(wait / 1000)}s`);
    await sleep(wait);
    return xget(token, path, params);
  }
  if (res.status === 401) throw new Error('401 unauthorized — check X_BEARER_TOKEN');
  if (res.status === 403) throw new Error('403 forbidden — your X API tier may not include read access (need Basic+)');
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`x api ${path} failed: ${res.status} ${body.slice(0, 200)}`);
  }
  return res.json();
}

// ---------- per-user dump ----------

async function resolveUser(token, handle) {
  const res = await xget(token, `/users/by/username/${handle}`, { 'user.fields': 'name,protected' });
  if (!res.data) throw new Error(`could not resolve X user @${handle}`);
  if (res.data.protected) throw new Error(`@${handle} is protected; cannot pull tweets`);
  return { id: res.data.id, handle: res.data.username, name: res.data.name };
}

async function dumpUserTimeline(token, user, max, includeReplies, out) {
  const exclude = includeReplies ? undefined : 'retweets,replies';
  let pulled = 0;
  let pagination_token;
  let earliest = null;
  let latest = null;
  let rateLimited = false;

  while (pulled < max) {
    const remaining = max - pulled;
    const params = {
      max_results: Math.min(100, Math.max(5, remaining)),
      'tweet.fields': 'created_at,public_metrics,referenced_tweets,in_reply_to_user_id',
    };
    if (exclude) params.exclude = exclude;
    if (pagination_token) params.pagination_token = pagination_token;

    let res;
    try {
      res = await xget(token, `/users/${user.id}/tweets`, params);
    } catch (err) {
      console.error(`error pulling @${user.handle}: ${err.message}`);
      break;
    }

    const tweets = res.data || [];
    if (tweets.length === 0) break;

    for (const t of tweets) {
      const refs = t.referenced_tweets || [];
      const replyRef = refs.find((r) => r.type === 'replied_to');
      const quoteRef = refs.find((r) => r.type === 'quoted');
      const kind = replyRef ? 'reply' : quoteRef ? 'quote' : 'post';
      out.write(JSON.stringify({
        id: t.id,
        author_handle: user.handle,
        author_name: user.name,
        created_at: t.created_at,
        text: t.text || '',
        kind,
        in_reply_to: replyRef?.id || null,
        quoted_id: quoteRef?.id || null,
        metrics: {
          retweets: t.public_metrics?.retweet_count ?? 0,
          likes: t.public_metrics?.like_count ?? 0,
          replies: t.public_metrics?.reply_count ?? 0,
          quotes: t.public_metrics?.quote_count ?? 0,
        },
        url: `https://x.com/${user.handle}/status/${t.id}`,
      }) + '\n');
      pulled++;
      if (!earliest || t.created_at < earliest) earliest = t.created_at;
      if (!latest || t.created_at > latest) latest = t.created_at;
    }

    pagination_token = res.meta?.next_token;
    if (!pagination_token) break;
  }

  return { handle: user.handle, name: user.name, count: pulled, earliest, latest, rateLimited };
}

// ---------- main ----------

async function main() {
  loadEnv();
  const args = parseArgs(process.argv.slice(2));
  const token = process.env.X_BEARER_TOKEN;
  if (!token) die('X_BEARER_TOKEN not set (in env or ./.env)');

  const storeRoot = process.env.PERSONA_HOME
    ? resolve(process.env.PERSONA_HOME)
    : resolve(process.cwd(), '.personas');
  const outDir = resolve(storeRoot, 'assets', args.slug);
  mkdirSync(outDir, { recursive: true });
  const out = createWriteStream(join(outDir, 'x-posts.jsonl'));

  const perUser = [];
  for (const handle of args.users) {
    console.error(`resolving @${handle}…`);
    const user = await resolveUser(token, handle);
    console.error(`dumping @${user.handle} (id ${user.id}), up to ${args.max} posts…`);
    const summary = await dumpUserTimeline(token, user, args.max, args.includeReplies, out);
    perUser.push(summary);
    console.error(`  → ${summary.count} posts`);
  }
  out.end();

  const metaPath = join(outDir, 'x-metadata.json');
  const meta = {
    slug: args.slug,
    source: 'x',
    dumped_at: new Date().toISOString(),
    users: perUser,
    include_replies: args.includeReplies,
    max_per_user: args.max,
    total_records: perUser.reduce((n, u) => n + u.count, 0),
  };
  await writeFile(metaPath, JSON.stringify(meta, null, 2));

  console.error(`done. ${meta.total_records} total posts across ${perUser.length} user(s) → ${outDir}`);
}

main().catch((err) => {
  console.error(`fatal: ${err.message}`);
  process.exit(1);
});
