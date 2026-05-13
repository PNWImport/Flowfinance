#!/usr/bin/env node
// Extract the inline <script> from flowfinance-beast.html and run eslint on it.
// Reports issues but does not write back (the file is hand-edited HTML).

import { readFileSync, writeFileSync, unlinkSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, '..');
const html = readFileSync(resolve(root, 'flowfinance-beast.html'), 'utf8');

// Find scripts; pick the largest (skip JSON-LD)
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const main = scripts.reduce((a, b) => (b.length > a.length ? b : a), '');

const tmp = resolve(root, '.app-extracted.js');
writeFileSync(tmp, main);

const args = ['--config', resolve(root, 'eslint.config.mjs'), tmp];
if (process.argv.includes('--fix')) args.unshift('--fix');
const result = spawnSync('eslint', args, { stdio: 'inherit', env: process.env });

try {
  unlinkSync(tmp);
} catch {
  /* ignore */
}

process.exit(result.status ?? 0);
