#!/usr/bin/env bash
# Daily refresh. Rebuilds data.js from source and leaves the previous copy in
# place if anything fails, so a bad upstream day cannot blank the dashboard.
#
#   ./refresh.sh                 rebuild from today
#   ./refresh.sh 2026-08-22      rebuild from a given date
#
# cron, every morning at 06:15:
#   15 6 * * * /path/to/refresh.sh >> /path/to/refresh.log 2>&1

set -euo pipefail
cd "$(dirname "$0")"

FROM="${1:-$(date +%F)}"
DAYS="${DAYS:-4}"
TOP="${TOP:-50}"
STAMP=$(date +%Y%m%dT%H%M%S)

mkdir -p archive
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "[$(date -Is)] building from $FROM ($DAYS days, top $TOP)"

# Build into a temp file first. openfootball is volunteer-maintained and a repo
# can be mid-rewrite when the cron fires; a half-written data.js is worse than
# yesterday's complete one.
if python3 build.py --days "$DAYS" --top "$TOP" --from "$FROM" --out "$TMP/data.json"; then
  python3 - "$TMP/data.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
n = sum(day["count"] for day in d["days"])
if n == 0:
    sys.exit("refused: build produced zero fixtures")
print(f"  {n} fixtures across {len(d['days'])} days")
PY
  [ -f data.js ] && cp data.js "archive/data-$STAMP.js"
  cp "$TMP/data.json" data.json
  python3 - <<'PY'
import json, os
d = json.load(open("data.json"))
with open("data.js", "w") as f:
    f.write("window.__FIXTURE_DATA__=")
    json.dump(d, f, separators=(",", ":"))
    f.write(";")
PY
  echo "[$(date -Is)] ok"
else
  echo "[$(date -Is)] build failed, keeping existing data.js" >&2
  exit 1
fi

# Keep a fortnight of snapshots so predictions can be scored against results later.
find archive -name 'data-*.js' -mtime +14 -delete 2>/dev/null || true
