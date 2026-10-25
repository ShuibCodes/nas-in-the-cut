#!/usr/bin/env bash
# Build the static site and mirror it into the Next.js public/ folder.
# PHP and Apache files are left out: Vercel cannot run them, and stats.php
# holds a private key that must never be served as a plain file.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PUBLIC="$ROOT/../public"

cd "$ROOT"
python3 build.py

rsync -a --delete \
  --exclude '*.php' \
  --exclude '.htaccess' \
  --exclude '_headers' \
  --exclude 'UPLOAD.txt' \
  --exclude 'data/' \
  --exclude '.DS_Store' \
  "$ROOT/dist/" "$PUBLIC/"

echo "published dist/ to $PUBLIC"
