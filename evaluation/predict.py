"""Evaluation harness, step 1: per-fixture probabilities from one checkout.

Runs from main (trusted). Imports the TARGET checkout's tune/engine/replay and
prices every fixture of a frozen snapshot through the shared walk-forward
replay, with that checkout's shipped calibration (nothing is refitted).
Writes one JSON line per fixture: key, probabilities, outcome. No metrics are
computed here: scoring happens in score_pair.py, also from main.

    python3 evaluation/predict.py --verify SNAPSHOT
    python3 evaluation/predict.py --repo DIR --snapshot SNAPSHOT --out FILE.jsonl --meta FILE.json

Meant to run with no network (unshare --net) and no secrets in the environment.
"""
import argparse, hashlib, json, os, sys

SPLITS = ("fit", "check")


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verify(path):
    """The snapshot's own sha256 recomputed here, independent of the checkout under test."""
    with open(path) as f:
        body = json.load(f)
    sha = digest({"data": body["data"], "current": body["current"]})
    if sha != body.get("sha256"):
        raise SystemExit(f"{path}: contents do not match its sha256; refusing to use it")
    return body, sha


def predict(repo, snapshot):
    body, sha = verify(snapshot)
    repo = os.path.abspath(repo)
    sys.path.insert(0, repo)
    for m in ("tune", "engine", "replay", "sources"):
        sys.modules.pop(m, None)
    import tune, engine as E                                   # the checkout under test
    data = {tuple(k.split("|")): [tuple(r) for r in v] for k, v in body["data"].items()}
    rows, excluded = [], {}
    for split in SPLITS:
        excluded[split] = [{"code": v["code"], "reasons": v["reasons"]} for v in tune.exclusions(data, split)]
        for lh, la, y, code, d, h, a in tune.lambdas(data, split, meta=True):
            p = tune.outcome(lh, la, E.RHO)
            t = tune.curve_T(max(p), E.CALIBRATION) if E.CALIBRATION else E.TEMPERATURE
            q = [max(x, 1e-12) ** (1 / t) for x in p]
            s = sum(q)
            rows.append({"key": f"{split}|{code}|{d}|{h}|{a}", "split": split,
                         "p": [round(x / s, 10) for x in q], "y": y})
    meta = {"snapshot_sha256": sha, "snapshot_created": body.get("created"),
            "rho": E.RHO, "temperature": E.TEMPERATURE, "calibration": E.CALIBRATION,
            "excluded": excluded, "fixtures": len(rows)}
    return rows, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", metavar="SNAPSHOT")
    ap.add_argument("--repo"); ap.add_argument("--snapshot"); ap.add_argument("--out"); ap.add_argument("--meta")
    a = ap.parse_args()
    if a.verify:
        print(verify(a.verify)[1]); return
    rows, meta = predict(a.repo, a.snapshot)
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    with open(a.meta, "w") as f:
        json.dump(meta, f, indent=1)
    print(f"{len(rows)} fixtures from {a.repo}", file=sys.stderr)


if __name__ == "__main__":
    main()
