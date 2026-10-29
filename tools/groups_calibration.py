#!/usr/bin/env python3
"""
Groups landed against their stated chance, cut by band. Advisory: reads
groupings-record.json, writes nothing, fits nothing (rule 1). 29 Oct 2026.

    python3 tools/groups_calibration.py

A group is a win only when every leg won. Cuts: stated group chance, leg
count, leg chance, and the leg sport. z is (won - expected) / sqrt(sum p(1-p)).
Standard library only.
"""
import json, math, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cut(rows):
    n = len(rows)
    if not n:
        return None
    w = sum(r[1] for r in rows)
    e = sum(r[0] for r in rows)
    v = sum(r[0] * (1 - r[0]) for r in rows)
    return n, w, e, (w - e) / math.sqrt(v) if v else 0.0


def show(title, buckets):
    print("\n" + title)
    print("%-22s %5s %5s %8s %6s" % ("", "n", "won", "expected", "z"))
    for k in sorted(buckets, key=str):
        c = cut(buckets[k])
        if c:
            print("%-22s %5d %5d %8.1f %6.2f" % (k, c[0], c[1], c[2], c[3]))


def main():
    rec = json.load(open(os.path.join(HERE, "groupings-record.json")))
    G, L, S, K, N = {}, {}, {}, {}, {}
    for day in rec["days"]:
        for g in day["groups"]:
            if g["status"] not in ("won", "lost"):
                continue
            row = (g["p"], 1 if g["status"] == "won" else 0)
            pb = "%d-%d%%" % (int(g["p"] * 100) // 10 * 10, int(g["p"] * 100) // 10 * 10 + 10)
            G.setdefault(pb, []).append(row)
            K.setdefault(g["name"], []).append(row)
            N.setdefault("%d legs" % len(g["legs"]), []).append(row)
            for l in g["legs"]:
                if l["status"] not in ("won", "lost"):
                    continue
                lr = (l["p"], 1 if l["status"] == "won" else 0)
                lb = "%d-%d%%" % (int(l["p"] * 100) // 5 * 5, int(l["p"] * 100) // 5 * 5 + 5)
                L.setdefault(lb, []).append(lr)
                S.setdefault(l["sport"], []).append(lr)
    show("Groups by stated chance", G)
    show("Groups by kind", K)
    show("Groups by leg count", N)
    show("Legs by stated chance", L)
    show("Legs by sport", S)


if __name__ == "__main__":
    main()
