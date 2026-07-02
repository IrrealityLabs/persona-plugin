#!/usr/bin/env node
// Dump Slack messages for persona distillation.
//
// Usage:
//   node dump-slack.mjs --slug <persona-slug> --user <username> [--months=12]
//   node dump-slack.mjs --slug <persona-slug> --channel <channel-name> [--months=12]
//
// Reads SLACK_USER_TOKEN from process.env or ./.env in the cwd.
// Writes to <store>/assets/<slug>/slack.jsonl and slack-metadata.json,
// where <store> is $PERSONA_HOME if set, else ./.personas in the cwd.
//
// slack.jsonl uses the universal asset row — {context, question, answer, source}:
// answer is the person's own verbatim message, question is the last thing someone
// else said before it (empty if unprompted), context is the channel/thread setting,
// source is a permalink (or slack:<channel_id>:<ts>) that resolves back to it.
//
// Requires Node 18+ (built-in fetch). No npm install needed.

import { readFileSync, existsSync, mkdirSync, createWriteStream } from 'node:fs';
import { join, resolve } from 'node:path';

// ---------- arg parsing ----------

function parseArgs(argv) {
  const out = { months: 12, users: [] };
  for (const arg of argv) {
    if (arg.startsWith('--slug=')) out.slug = arg.slice(7);
    else if (arg === '--slug') throw new Error('use --slug=<value>');
    else if (arg.startsWith('--user=')) out.users.push(arg.slice(7));
    else if (arg.startsWith('--channel=')) out.channel = arg.slice(10);
    else if (arg.startsWith('--months=')) out.months = Number(arg.slice(9));
    else if (!arg.startsWith('--')) {
      // also accept positional --slug value forms
      if (!out.slug) out.slug = arg;
    }
  }
  if (!out.slug) die('missing --slug=<persona-slug>');
  if (out.users.length === 0 && !out.channel) die('need --user=<name> or --channel=<name>');
  if (out.users.length > 0 && out.channel) die('use --user OR --channel, not both');
  if (!Number.isFinite(out.months) || out.months <= 0) die(`invalid --months: ${out.months}`);
  return out;
}

function die(msg) {
  console.error(`error: ${msg}`);
  console.error('usage: node dump-slack.mjs --slug=<slug> (--user=<name> | --channel=<name>) [--months=12]');
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

// ---------- Slack client ----------

const SLACK_BASE = 'https://slack.com/api';

async function slack(token, method, params = {}) {
  // GET form with query string; works for all read endpoints we use.
  const url = new URL(`${SLACK_BASE}/${method}`);
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
  }
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const body = await res.json();
  if (!body.ok) throw new Error(`slack ${method} failed: ${body.error || res.status}`);
  // Honor rate-limit headers softly
  const retry = res.headers.get('retry-after');
  if (retry) await sleep(Number(retry) * 1000);
  return body;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ---------- user resolution ----------

async function resolveUser(token, target) {
  const want = target.toLowerCase().replace(/^@/, '');
  let cursor;
  do {
    const res = await slack(token, 'users.list', { limit: 200, cursor });
    for (const m of res.members || []) {
      if (m.deleted || m.is_bot) continue;
      const candidates = [
        m.name,
        m.profile?.display_name,
        m.profile?.display_name_normalized,
        m.profile?.real_name,
        m.profile?.real_name_normalized,
      ].filter(Boolean).map((s) => s.toLowerCase());
      if (candidates.some((c) => c === want || c.split(/\s+/)[0] === want)) {
        return {
          id: m.id,
          name: m.name,
          real_name: m.profile?.real_name || m.real_name || m.name,
        };
      }
    }
    cursor = res.response_metadata?.next_cursor;
  } while (cursor);
  throw new Error(`could not resolve Slack user "${target}"`);
}

async function resolveChannel(token, target) {
  const want = target.toLowerCase().replace(/^#/, '');
  let cursor;
  do {
    const res = await slack(token, 'conversations.list', {
      limit: 200,
      cursor,
      types: 'public_channel,private_channel',
      exclude_archived: true,
    });
    for (const c of res.channels || []) {
      if ((c.name || '').toLowerCase() === want) return { id: c.id, name: c.name };
    }
    cursor = res.response_metadata?.next_cursor;
  } while (cursor);
  throw new Error(`could not resolve channel "#${target}"`);
}

// ---------- name cache ----------

class NameCache {
  constructor(token) {
    this.token = token;
    this.cache = new Map();
  }
  async lookup(userId) {
    if (!userId) return null;
    if (this.cache.has(userId)) return this.cache.get(userId);
    try {
      const res = await slack(this.token, 'users.info', { user: userId });
      const name = res.user?.profile?.display_name || res.user?.name || userId;
      this.cache.set(userId, name);
      return name;
    } catch {
      this.cache.set(userId, userId);
      return userId;
    }
  }
}

// ---------- thread expansion ----------

async function fetchThread(token, channelId, threadTs, nameCache) {
  let cursor;
  const all = [];
  do {
    const res = await slack(token, 'conversations.replies', {
      channel: channelId,
      ts: threadTs,
      limit: 200,
      cursor,
    });
    for (const m of res.messages || []) {
      all.push({
        ts: m.ts,
        user: m.user || null,
        user_name: await nameCache.lookup(m.user),
        text: m.text || '',
      });
    }
    cursor = res.response_metadata?.next_cursor;
  } while (cursor);
  return all;
}

// ---------- universal asset rows ----------

const truncate = (s, n) => (s.length > n ? s.slice(0, n - 1) + '…' : s);

const safeOrigin = (permalink) => {
  try { return new URL(permalink).origin; } catch { return null; }
};

function messageLink(origin, channelId, ts) {
  return origin
    ? `${origin}/archives/${channelId}/p${ts.replace('.', '')}`
    : `slack:${channelId}:${ts}`;
}

// One row per emitted message in a thread. question = nearest preceding message
// by a different speaker; context carries the channel and the thread root.
function threadRows({ msgs, channelName, channelId, origin, shouldEmit, speakerInContext }) {
  const rows = [];
  const root = msgs[0];
  for (let i = 0; i < msgs.length; i++) {
    const m = msgs[i];
    if (!m.text || !shouldEmit(m)) continue;
    let question = '';
    for (let j = i - 1; j >= 0; j--) {
      if (msgs[j].user !== m.user && msgs[j].text) { question = msgs[j].text; break; }
    }
    let context = `Slack #${channelName}`;
    if (m !== root && root.text && root.user !== m.user) {
      context += ` — thread started by ${root.user_name || 'someone'}: "${truncate(root.text, 160)}"`;
    }
    if (speakerInContext) context += ` — said by ${m.user_name || 'unknown'}`;
    rows.push({ context, question, answer: m.text, source: messageLink(origin, channelId, m.ts) });
  }
  return rows;
}

// ---------- mode A: dump user messages ----------

async function dumpUser(token, slug, username, months, outDir) {
  const user = await resolveUser(token, username);
  console.error(`resolved user: @${user.name} (${user.id})`);
  const nameCache = new NameCache(token);
  const sinceUnix = Math.floor(Date.now() / 1000) - months * 30 * 24 * 3600;
  const sinceISO = new Date(sinceUnix * 1000).toISOString().slice(0, 10);

  const out = createWriteStream(join(outDir, 'slack.jsonl'));
  let total = 0;
  let threads = 0;
  let standalones = 0;
  let rows = 0;
  let capped = false;
  let origin = null;
  const seenThreads = new Set();
  const channels = new Map();

  let page = 1;
  let maxPages = 100; // ~10K results
  while (page <= maxPages) {
    const res = await slack(token, 'search.messages', {
      query: `from:@${user.name} after:${sinceISO}`,
      count: 100,
      page,
    });
    const matches = res.messages?.matches || [];
    if (matches.length === 0) break;
    for (const m of matches) {
      total++;
      const channelId = m.channel?.id;
      const channelName = m.channel?.name || 'unknown';
      channels.set(channelId, channelName);
      if (!origin && m.permalink) origin = safeOrigin(m.permalink);
      if (m.thread_ts) {
        // any thread message — expand once from the root
        const key = `${channelId}:${m.thread_ts}`;
        if (seenThreads.has(key)) continue;
        seenThreads.add(key);
        const msgs = await fetchThread(token, channelId, m.thread_ts, nameCache);
        for (const row of threadRows({
          msgs, channelName, channelId, origin,
          shouldEmit: (x) => x.user === user.id,
        })) {
          out.write(JSON.stringify(row) + '\n');
          rows++;
        }
        threads++;
      } else if (m.text) {
        out.write(JSON.stringify({
          context: `Slack #${channelName}`,
          question: '',
          answer: m.text,
          source: m.permalink || messageLink(origin, channelId, m.ts),
        }) + '\n');
        rows++;
        standalones++;
      }
    }
    const totalPages = res.messages?.paging?.pages || 1;
    if (page >= totalPages) break;
    if (page === maxPages) capped = true;
    page++;
  }
  out.end();

  return {
    mode: 'user',
    target: { username: user.name, user_id: user.id, real_name: user.real_name },
    months_covered: months,
    date_range: { from: sinceISO, to: new Date().toISOString().slice(0, 10) },
    total_records: total,
    rows,
    threads,
    standalones,
    channels: [...channels.entries()].map(([id, name]) => ({ id, name })),
    search_capped: capped,
  };
}

// ---------- mode B: dump channel messages ----------

async function dumpChannel(token, slug, channelName, months, outDir) {
  const channel = await resolveChannel(token, channelName);
  console.error(`resolved channel: #${channel.name} (${channel.id})`);
  const nameCache = new NameCache(token);
  const sinceUnix = Math.floor(Date.now() / 1000) - months * 30 * 24 * 3600;

  const out = createWriteStream(join(outDir, 'slack.jsonl'));
  let total = 0;
  let threads = 0;
  let standalones = 0;
  let rows = 0;
  const userCounts = new Map();

  let cursor;
  do {
    const res = await slack(token, 'conversations.history', {
      channel: channel.id,
      limit: 200,
      cursor,
      oldest: sinceUnix,
    });
    for (const m of res.messages || []) {
      if (m.subtype && m.subtype !== 'thread_broadcast') continue;
      total++;
      const u = m.user || null;
      if (u) userCounts.set(u, (userCounts.get(u) || 0) + 1);
      if (m.thread_ts && m.reply_count) {
        const msgs = await fetchThread(token, channel.id, m.thread_ts, nameCache);
        for (const row of threadRows({
          msgs, channelName: channel.name, channelId: channel.id, origin: null,
          shouldEmit: (x) => !!x.text,
          speakerInContext: true, // channel dumps aggregate many voices
        })) {
          out.write(JSON.stringify(row) + '\n');
          rows++;
        }
        threads++;
      } else if (m.text) {
        out.write(JSON.stringify({
          context: `Slack #${channel.name} — said by ${await nameCache.lookup(u) || 'unknown'}`,
          question: '',
          answer: m.text,
          source: messageLink(null, channel.id, m.ts),
        }) + '\n');
        rows++;
        standalones++;
      }
    }
    cursor = res.response_metadata?.next_cursor;
  } while (cursor);
  out.end();

  const topContributors = [...userCounts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 20);
  const contributors = await Promise.all(
    topContributors.map(async ([id, count]) => ({
      user_id: id,
      user_name: await nameCache.lookup(id),
      message_count: count,
    }))
  );

  return {
    mode: 'channel',
    target: { channel: channel.name, channel_id: channel.id },
    months_covered: months,
    date_range: {
      from: new Date(sinceUnix * 1000).toISOString().slice(0, 10),
      to: new Date().toISOString().slice(0, 10),
    },
    total_records: total,
    rows,
    threads,
    standalones,
    top_contributors: contributors,
  };
}

// ---------- main ----------

async function main() {
  loadEnv();
  const args = parseArgs(process.argv.slice(2));
  const token = process.env.SLACK_USER_TOKEN;
  if (!token) die('SLACK_USER_TOKEN not set (in env or ./.env)');
  if (!token.startsWith('xoxp-')) die('SLACK_USER_TOKEN must be a user token (xoxp-...)');

  const storeRoot = process.env.PERSONA_HOME
    ? resolve(process.env.PERSONA_HOME)
    : resolve(process.cwd(), '.personas');
  const outDir = resolve(storeRoot, 'assets', args.slug);
  mkdirSync(outDir, { recursive: true });

  let metaSource;
  if (args.channel) {
    metaSource = await dumpChannel(token, args.slug, args.channel, args.months, outDir);
  } else {
    // For now, single --user; multiple users for a single slug should re-run with same slug
    // and we'd append, but simplest: just dump the first user. Multi-user aggregation is an
    // explicit choice; document in slack-source.md if you add it.
    if (args.users.length > 1) {
      console.error('note: --user can be passed once for slack dump; for multi-user aggregation re-run per user and concatenate manually');
    }
    metaSource = await dumpUser(token, args.slug, args.users[0], args.months, outDir);
  }

  const metaPath = join(outDir, 'slack-metadata.json');
  const meta = {
    slug: args.slug,
    source: 'slack',
    dumped_at: new Date().toISOString(),
    ...metaSource,
  };
  await import('node:fs/promises').then((fs) => fs.writeFile(metaPath, JSON.stringify(meta, null, 2)));

  console.error(`done. ${metaSource.rows} rows from ${metaSource.total_records} records (${metaSource.threads} threads, ${metaSource.standalones} standalone) → ${outDir}/slack.jsonl`);
}

main().catch((err) => {
  console.error(`fatal: ${err.message}`);
  process.exit(1);
});
