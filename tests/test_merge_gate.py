"""Regression tests for the office merge gate (agents/merge_gate.decide).

    python3 -m unittest tests.test_merge_gate -v

Standard library only, no network. The gate must fail closed: stale labels,
stale or missing CI, unknown mergeability, approvals of older commits and
approvals from bots must all hold a pull request.
"""
import os, sys, unittest
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "agents"))
import merge_gate as G

POLICY = G.load_policy()
NOW = datetime(2026, 10, 3, 21, 0, tzinfo=timezone.utc)
SHA, OLD = "a" * 40, "b" * 40
BASE = "c" * 40


def pr(files=("claude/note.md",), sha=SHA, labels=("office-agent", "checks-passed", "auto-merge-ok"), age_h=20,
       mergeable="MERGEABLE", state="CLEAN"):
    return {"number": 7, "headRefOid": sha, "createdAt": (NOW - timedelta(hours=age_h)).isoformat(),
            "labels": list(labels), "files": list(files), "mergeable": mergeable, "mergeStateStatus": state}


def run(name, sha=SHA, status="completed", conclusion="success", app=15368, started="2026-10-03T08:00:00Z"):
    return {"name": name, "head_sha": sha, "status": status, "conclusion": conclusion,
            "app": {"id": app}, "started_at": started}


def green(sha=SHA):
    return [run(n, sha) for n in POLICY["required_checks"]]


def evidence(sha=SHA, verdict="n/a"):
    return {"candidate_sha": sha, "base_sha": BASE, "verdict": verdict}


def review(sha=SHA, login="douglasbakeronline", assoc="OWNER", state="APPROVED"):
    return {"state": state, "user": {"login": login}, "author_association": assoc, "commit_id": sha}


def decide(p, checks=None, reviews=(), ev="default", drift=()):
    return G.decide(p, green() if checks is None else checks, list(reviews), POLICY, NOW,
                    evidence() if ev == "default" else ev, None if drift is None else list(drift))


class Happy(unittest.TestCase):
    def test_docs_only_all_green_merges(self):
        ok, why = decide(pr())
        self.assertTrue(ok, why)

    def test_model_change_with_evaluation_pass_merges_without_review(self):
        ok, why = decide(pr(files=["engine.py"]), ev=evidence(verdict="pass"))
        self.assertTrue(ok, why)

    def test_ui_tests_sources_merge_without_review(self):
        for f in ("index.html", "tests/test_x.py", "sources.py", "mystery.txt"):
            ok, why = decide(pr(files=[f]))
            self.assertTrue(ok, (f, why))

    def test_bot_only_drift_on_main_is_fine(self):
        ok, why = decide(pr(), drift=[{"sha": "d" * 40, "files": ["predictions/2026-10-03.json", "record.json"]}])
        self.assertTrue(ok, why)


class StaleLabels(unittest.TestCase):
    def test_label_with_failed_check_holds(self):
        checks = green(); checks[0]["conclusion"] = "failure"
        ok, why = decide(pr(), checks=checks)
        self.assertFalse(ok); self.assertTrue(any("concluded failure" in r for r in why))

    def test_label_with_no_checks_holds(self):
        ok, why = decide(pr(), checks=[])
        self.assertFalse(ok); self.assertTrue(any("missing" in r for r in why))

    def test_labels_alone_never_approve(self):
        ok, _ = decide(pr(labels=("office-agent", "checks-passed", "auto-merge-ok", "approved")), checks=[], ev=None)
        self.assertFalse(ok)

    def test_hold_label_holds(self):
        ok, why = decide(pr(labels=("office-agent", "hold")))
        self.assertFalse(ok); self.assertIn("on hold", why)


class StaleCI(unittest.TestCase):
    def test_success_on_older_sha_holds(self):
        ok, why = decide(pr(), checks=green(OLD))
        self.assertFalse(ok); self.assertTrue(all("missing" in r for r in why if "check" in r))

    def test_newer_failure_beats_older_success(self):
        checks = green() + [run("evaluation", conclusion="failure", started="2026-10-03T09:00:00Z")]
        ok, why = decide(pr(), checks=checks)
        self.assertFalse(ok)

    def test_pending_neutral_skipped_hold(self):
        for status, concl in (("in_progress", None), ("queued", None), ("completed", "neutral"),
                              ("completed", "skipped"), ("completed", "cancelled"), ("completed", None)):
            checks = green(); checks[1] = run(checks[1]["name"], status=status, conclusion=concl)
            ok, _ = decide(pr(), checks=checks)
            self.assertFalse(ok, (status, concl))

    def test_check_from_other_app_is_ignored(self):
        checks = [run(n, app=999) for n in POLICY["required_checks"]]
        ok, _ = decide(pr(), checks=checks)
        self.assertFalse(ok)

    def test_evidence_for_other_commit_holds(self):
        ok, why = decide(pr(), ev=evidence(sha=OLD))
        self.assertFalse(ok)

    def test_missing_evidence_holds(self):
        ok, _ = decide(pr(), ev=None)
        self.assertFalse(ok)

    def test_insufficient_or_failed_verdict_holds(self):
        for v in ("insufficient", "fail", None, "PASS"):
            ok, _ = decide(pr(), ev=evidence(verdict=v))
            self.assertFalse(ok, v)

    def test_non_bot_commit_on_main_since_base_holds(self):
        ok, why = decide(pr(), drift=[{"sha": "e" * 40, "files": ["engine.py"]}])
        self.assertFalse(ok); self.assertTrue(any("re-run evaluation" in r for r in why))

    def test_unknown_drift_holds(self):
        ok, _ = decide(pr(), drift=None)
        self.assertFalse(ok)


class Mergeability(unittest.TestCase):
    def test_unknown_or_conflicting_holds(self):
        for m, st in (("UNKNOWN", "UNKNOWN"), ("CONFLICTING", "DIRTY"), (None, None), ("MERGEABLE", "BEHIND"),
                      ("MERGEABLE", "BLOCKED")):
            ok, _ = decide(pr(mergeable=m, state=st))
            self.assertFalse(ok, (m, st))

    def test_no_waiting_period(self):
        ok, why = decide(pr(age_h=0))
        self.assertTrue(ok, why)


class OwnerApproval(unittest.TestCase):
    def test_workflow_security_needs_owner(self):
        for f in (".github/workflows/x.yml", "agents/merge_gate.py", "agents/policy.json", "CLAUDE.md"):
            ok, why = decide(pr(files=[f]))
            self.assertFalse(ok, f); self.assertTrue(any("owner approval" in r for r in why), f)

    def test_model_change_needs_pass_not_na(self):
        for f in ("engine.py", "calibration.json", "tune.py"):
            ok, why = decide(pr(files=[f]))
            self.assertFalse(ok, f); self.assertTrue(any("evaluation pass" in r for r in why), f)

    def test_model_file_with_identical_predictions_merges(self):
        ev = evidence(verdict="n/a")
        ev["splits"] = {"check": {"paired": {"n": 300, "identical": True}}, "fit": {"paired": {"n": 6000, "identical": True}}}
        ok, why = decide(pr(files=["sports.py", "score_tennis.py"]), ev=ev)
        self.assertTrue(ok, why)

    def test_identical_needs_a_scored_check_split(self):
        for splits in ({}, {"check": {"paired": {"n": 0, "identical": True}}},
                       {"check": {"paired": {"n": 300, "identical": True}}, "fit": {"paired": {"n": 9, "identical": False}}}):
            ev = evidence(verdict="n/a"); ev["splits"] = splits
            ok, _ = decide(pr(files=["engine.py"]), ev=ev)
            self.assertFalse(ok, splits)

    def test_approval_of_older_commit_holds(self):
        ok, _ = decide(pr(files=["agents/open_pr.sh"]), reviews=[review(sha=OLD)])
        self.assertFalse(ok)

    def test_owner_approval_of_head_merges_workflow_change(self):
        ok, why = decide(pr(files=["agents/open_pr.sh"]), reviews=[review()])
        self.assertTrue(ok, why)

    def test_bot_approval_does_not_count(self):
        for r in (review(login="github-actions[bot]", assoc="NONE"), review(login="github-actions[bot]"),
                  review(assoc="CONTRIBUTOR"), review(state="COMMENTED")):
            ok, _ = decide(pr(files=["agents/open_pr.sh"]), reviews=[r])
            self.assertFalse(ok, r)

    def test_docs_plus_model_file_needs_pass(self):
        ok, _ = decide(pr(files=["claude/note.md", "engine.py"]))
        self.assertFalse(ok)
        ok, why = decide(pr(files=["claude/note.md", "engine.py"]), ev=evidence(verdict="pass"))
        self.assertTrue(ok, why)


if __name__ == "__main__":
    unittest.main()
