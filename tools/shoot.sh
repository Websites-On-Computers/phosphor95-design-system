#!/usr/bin/env bash
# Screenshot the gallery in headless Firefox (snap-safe: profile and output live under dist/).
#   tools/shoot.sh [theme] [width] [height] [extra-query]   (site must be served on :8095)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
theme="${1:-green}"; w="${2:-1280}"; h="${3:-3000}"; q="${4:-}"
mkdir -p "$ROOT/dist/shots" "$ROOT/dist/ffprofile"
out="$ROOT/dist/shots/gallery-$theme-${w}${q:+-${q//[^a-z]/}}.png"
timeout 90 firefox --headless --no-remote --profile "$ROOT/dist/ffprofile" \
  --window-size="$w,$h" --screenshot "$out" "http://localhost:8095/?theme=$theme${q:+&$q}" >/dev/null 2>&1 || true
[ -s "$out" ] && echo "$out" || { echo "screenshot failed" >&2; exit 1; }
