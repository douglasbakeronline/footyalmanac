#!/usr/bin/env bash
# Office agents: verify the agent's working-tree changes and open a pull request.
set -uo pipefail
KEY="$1"; OWNER="$2"; TITLE="$3"
PROTECTED="record.json predictions predictions-sports predictions-tennis current history history-sports dashboard.html adjustments.json calibration.json tuning-report.json sports-record.json sports-record.js tennis-record.json tennis-record.js .github"
restore() { for p in $PROTECTED; do git checkout -q HEAD -- "$p" 2>/dev/null || true; git clean -fdq -- "$p" 2>/dev/null || true; done; rm -f data.js data.json; }

restore
git add -A
if git diff --cached --quiet; then echo "The agent made no changes."; exit 0; fi

CHECKS="passed"
python3 nametest.py > /tmp/office-agent/nametest.log 2>&1 || CHECKS="failed"
if git diff --cached --name-only | grep -qE '^(build|engine|sources|rankings|predictability|score|odds|backfill)\.py$'; then
  python3 build.py --days 2 --no-topup --no-odds > /tmp/office-agent/build.log 2>&1 || CHECKS="failed"
fi
restore; git add -A

META=/tmp/office-agent/meta.json; [ -f "$META" ] || echo '{"type":"code","gates":"n/a","automerge":false,"summary":"No summary written."}' > "$META"
TYPE=$(python3 -c "import json;print(json.load(open('$META')).get('type','code'))")
AUTO=$(python3 -c "import json;m=json.load(open('$META'));print('yes' if m.get('automerge') and m.get('type')!='ui' and m.get('gates')!='failed' else 'no')")
SUMMARY=$(python3 -c "import json;print(json.load(open('$META')).get('summary',''))")

BRANCH="office-agent/$(date -u +%Y-%m-%d)-${KEY}"
git checkout -q -b "$BRANCH"
git -c user.name="footyalmanac-hq[bot]" -c user.email="41898282+github-actions[bot]@users.noreply.github.com" commit -q -m "Office agent ($OWNER): $TITLE"
git push -q origin "$BRANCH"

for L in "office-agent:5b4bd6" "agent:$OWNER:f0b35a" "objective:$KEY:c5def5" "checks-$CHECKS:$([ $CHECKS = passed ] && echo 0e8a16 || echo d93f0b)" "auto-merge-ok:0e8a16" "needs-owner:fbca04" "hold:b60205"; do
  gh label create "${L%:*}" --color "${L##*:}" --force >/dev/null 2>&1 || true
done
LABELS="office-agent,agent:$OWNER,objective:$KEY,checks-$CHECKS"
if [ "$AUTO" = yes ] && [ "$CHECKS" = passed ]; then LABELS="$LABELS,auto-merge-ok"; NOTE="This will merge automatically at the next merge window (22:00 UK) if it is at least 12 hours old. Add the **hold** label or close it to stop that."; else LABELS="$LABELS,needs-owner"; NOTE="This one waits for the owner: it is a $TYPE change, checks $CHECKS, auto-merge was not recommended."; fi
CLOSES=""; case "$KEY" in issue-*) CLOSES="Closes #${KEY#issue-}";; esac
BODY=$( { echo "> **Office agent:** $OWNER · type: $TYPE · checks: $CHECKS"; echo ">"; echo "> $SUMMARY"; echo ">"; echo "> $NOTE"; echo; [ -n "$CLOSES" ] && { echo "$CLOSES"; echo; }; cat /tmp/office-agent/report.md 2>/dev/null || echo "(no report written)"; } )
gh pr create --base main --head "$BRANCH" --title "[$OWNER] $TITLE" --body "$BODY" --label "$LABELS"
