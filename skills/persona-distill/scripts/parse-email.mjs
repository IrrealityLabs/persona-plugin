#!/usr/bin/env node
// Parse an email archive into the same thread-record shape dump-slack.mjs emits,
// so the distiller's C/Q/A extraction works on email exactly like Slack.
//
// Handles .eml (one message), .mbox (many), or a .txt export. Groups messages into
// threads by normalized subject, decodes quoted-printable / base64 bodies, strips
// quoted reply text, and tags each message with its sender.
//
// Usage:
//   node parse-email.mjs --slug=<slug> --file=<path.eml|.mbox|.txt> --target="<name or email>"
//
// Writes ./.personas/assets/<slug>/email-messages.jsonl and email-metadata.json.
// Node 18+. No npm install. The persona is identified by --target (whose messages are
// the "answers" the distiller learns from).

import { readFileSync, existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

// ---------- args ----------

function parseArgs(argv) {
  const out = {};
  for (const a of argv) {
    if (a.startsWith('--slug=')) out.slug = a.slice(7);
    else if (a.startsWith('--file=')) out.file = a.slice(7);
    else if (a.startsWith('--target=')) out.target = a.slice(9);
  }
  if (!out.slug) die('missing --slug=<persona-slug>');
  if (!out.file) die('missing --file=<path to .eml/.mbox/.txt>');
  if (!out.target) die('missing --target="<name or email>" — whose messages is this persona?');
  return out;
}

function die(msg) {
  console.error(`error: ${msg}`);
  console.error('usage: node parse-email.mjs --slug=<slug> --file=<path> --target="<name|email>"');
  process.exit(1);
}

// ---------- mbox / message splitting ----------

// Split an mbox into raw message blocks on the "From " separator lines; a lone .eml
// has no separator and comes back as a single block.
function splitMessages(raw) {
  const lines = raw.split(/\r?\n/);
  const blocks = [];
  let cur = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const isSep = /^From \S+.*\d{4}/.test(line) && (i === 0 || lines[i - 1] === '');
    if (isSep && cur.length) {
      blocks.push(cur.join('\n'));
      cur = [];
    }
    if (isSep) continue; // drop the mbox separator line itself
    cur.push(line);
  }
  if (cur.length) blocks.push(cur.join('\n'));
  return blocks.map((b) => b.trim()).filter(Boolean);
}

// ---------- header parsing ----------

function splitHeadersBody(block) {
  const idx = block.search(/\r?\n\r?\n/);
  if (idx === -1) return { headerText: block, body: '' };
  return { headerText: block.slice(0, idx), body: block.slice(idx).replace(/^\r?\n\r?\n/, '') };
}

function parseHeaders(headerText) {
  // unfold continuation lines (leading whitespace continues the previous header)
  const unfolded = headerText.replace(/\r?\n[ \t]+/g, ' ');
  const headers = {};
  for (const line of unfolded.split(/\r?\n/)) {
    const m = line.match(/^([\w-]+):\s*(.*)$/);
    if (m) headers[m[1].toLowerCase()] = m[2].trim();
  }
  return headers;
}

// "Mike Reyes" <mike@x.com>  ->  { name: "Mike Reyes", email: "mike@x.com" }
function parseFrom(from) {
  if (!from) return { name: '', email: '' };
  const m = from.match(/^\s*"?([^"<]*?)"?\s*<([^>]+)>\s*$/);
  if (m) return { name: m[1].trim(), email: m[2].trim().toLowerCase() };
  if (from.includes('@')) return { name: '', email: from.trim().toLowerCase() };
  return { name: from.trim(), email: '' };
}

// ---------- body decoding ----------

function decodeQuotedPrintable(s) {
  return s
    .replace(/=\r?\n/g, '') // soft line breaks
    .replace(/=([0-9A-Fa-f]{2})/g, (_, h) => String.fromCharCode(parseInt(h, 16)));
}

function decodeBody(body, headers) {
  const cte = (headers['content-transfer-encoding'] || '').toLowerCase();
  const ctype = (headers['content-type'] || '').toLowerCase();

  // multipart: pick the first text/plain part (fall back to text/html, stripped)
  const boundaryMatch = (headers['content-type'] || '').match(/boundary="?([^";]+)"?/i);
  if (ctype.startsWith('multipart/') && boundaryMatch) {
    const boundary = boundaryMatch[1];
    const parts = body.split(new RegExp(`--${boundary.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?:--)?\\s*`));
    let html = null;
    for (const part of parts) {
      if (!part.trim()) continue;
      const { headerText, body: pBody } = splitHeadersBody(part);
      const pHeaders = parseHeaders(headerText);
      const pType = (pHeaders['content-type'] || '').toLowerCase();
      if (pType.startsWith('text/plain')) return decodeBody(pBody, pHeaders);
      if (pType.startsWith('text/html') && html === null) html = decodeBody(pBody, pHeaders);
    }
    if (html !== null) return stripHtml(html);
    return '';
  }

  let text = body;
  if (cte === 'base64') {
    try { text = Buffer.from(body.replace(/\s+/g, ''), 'base64').toString('utf8'); } catch { /* keep raw */ }
  } else if (cte === 'quoted-printable') {
    text = decodeQuotedPrintable(body);
  }
  if (ctype.startsWith('text/html')) text = stripHtml(text);
  return text;
}

function stripHtml(html) {
  return html
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(p|div|li|tr|h[1-6])>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

// Drop quoted reply text so a turn's body is what *this* person wrote, not the history.
function stripQuotes(text) {
  const out = [];
  for (const line of text.split('\n')) {
    if (/^\s*>/.test(line)) continue; // quoted line
    if (/^\s*On .+wrote:\s*$/.test(line)) break; // "On <date>, X wrote:"
    if (/^-{2,}\s*Original Message\s*-{2,}/i.test(line)) break;
    if (/^\s*From:.*\bSent:/i.test(line)) break;
    out.push(line);
  }
  return out.join('\n').replace(/\n{3,}/g, '\n\n').trim();
}

// ---------- threading ----------

const normalizeSubject = (s) =>
  (s || '(no subject)').replace(/^\s*((re|fwd?|aw|sv)\s*:\s*)+/i, '').trim().toLowerCase() || '(no subject)';

const senderName = (f) => f.name || (f.email ? f.email.split('@')[0] : 'unknown');

function isTarget(from, target) {
  const t = target.toLowerCase().replace(/^[@<]|>$/g, '');
  return (
    (from.email && (from.email === t || from.email.split('@')[0] === t)) ||
    (from.name && (from.name.toLowerCase() === t || from.name.toLowerCase().split(/\s+/)[0] === t))
  );
}

// ---------- main ----------

function main() {
  const args = parseArgs(process.argv.slice(2));
  const path = resolve(process.cwd(), args.file);
  if (!existsSync(path)) die(`file not found: ${args.file}`);

  const raw = readFileSync(path, 'utf8');
  const blocks = splitMessages(raw);

  const messages = [];
  let targetSeen = 0;
  for (const block of blocks) {
    const { headerText, body } = splitHeadersBody(block);
    const headers = parseHeaders(headerText);
    const from = parseFrom(headers.from);
    const text = stripQuotes(decodeBody(body, headers));
    if (!text) continue;
    const ts = headers.date ? new Date(headers.date).toISOString().replace('Invalid Date', '') : '';
    if (isTarget(from, args.target)) targetSeen++;
    messages.push({
      subject: headers.subject || '',
      norm: normalizeSubject(headers.subject),
      user_name: senderName(from),
      email: from.email,
      ts: Number.isNaN(Date.parse(headers.date)) ? '' : new Date(headers.date).toISOString(),
      text,
    });
  }

  if (messages.length === 0) die('no readable messages parsed from the file');
  if (targetSeen === 0) {
    console.error(`warning: no messages matched --target="${args.target}". Check the name/email; senders seen:`);
    console.error('  ' + [...new Set(messages.map((m) => `${m.user_name} <${m.email}>`))].slice(0, 15).join('\n  '));
  }

  // group into threads by normalized subject, order each by timestamp
  const byThread = new Map();
  for (const m of messages) {
    if (!byThread.has(m.norm)) byThread.set(m.norm, []);
    byThread.get(m.norm).push(m);
  }

  const outDir = resolve(process.cwd(), '.personas', 'assets', args.slug);
  mkdirSync(outDir, { recursive: true });
  const lines = [];
  let threadCount = 0;
  for (const [, msgs] of byThread) {
    msgs.sort((a, b) => (a.ts || '').localeCompare(b.ts || ''));
    lines.push(JSON.stringify({
      kind: 'thread',
      channel_name: 'email',
      subject: msgs[0].subject,
      messages: msgs.map((m) => ({ ts: m.ts, user_name: m.user_name, text: m.text })),
    }));
    threadCount++;
  }
  writeFileSync(join(outDir, 'email-messages.jsonl'), lines.join('\n') + '\n');

  const tgt = parseFrom(args.target.includes('@') ? `<${args.target}>` : args.target);
  const dates = messages.map((m) => m.ts).filter(Boolean).sort();
  const meta = {
    slug: args.slug,
    source: 'email',
    dumped_at: new Date().toISOString(),
    source_file: args.file,
    target: { name: tgt.name || args.target, email: tgt.email },
    total_messages: messages.length,
    target_messages: targetSeen,
    threads: threadCount,
    date_range: dates.length ? { from: dates[0].slice(0, 10), to: dates[dates.length - 1].slice(0, 10) } : null,
  };
  writeFileSync(join(outDir, 'email-metadata.json'), JSON.stringify(meta, null, 2));

  console.error(`done. ${messages.length} messages (${targetSeen} from target) in ${threadCount} threads → ${outDir}`);
}

main();
