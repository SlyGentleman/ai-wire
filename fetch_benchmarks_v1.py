#!/usr/bin/env python3
"""
Path A - Phase 1
Fetch + normalize SWE-bench leaderboards into a canonical benchmarks.json

Source:
- SWE-bench website repo stores leaderboards at data/leaderboards.json
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests

OUTPUT = os.path.expanduser("~/Desktop/ai_wire_v2/benchmarks.json")

SWE_BENCH_URL = "https://raw.githubusercontent.com/SWE-bench/swe-bench.github.io/master/data/leaderboards.json"



def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_float(x):
    try:
        return float(x)
    except Exception:
        return None


def main():
    try:
        r = requests.get(SWE_BENCH_URL, timeout=30)
        r.raise_for_status()
        raw = r.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch SWE-bench leaderboards: {e}", file=sys.stderr)
        sys.exit(1)

    # Canonical output schema (yours)
    out = {
        "last_updated": now_utc_iso(),
        "sources": [
            {
                "id": "swebench",
                "name": "SWE-bench",
                "url": "https://www.swebench.com/",
                "data_url": SWE_BENCH_URL,
            }
        ],
        "benchmarks": []
    }

    leaderboards = raw.get("leaderboards", [])
    for lb in leaderboards:
        lb_name = lb.get("name", "Unknown")
        results = lb.get("results", [])

        bench_id = f"swebench_{lb_name.lower().replace(' ', '_')}"
        bench = {
            "id": bench_id,
            "name": f"SWE-bench {lb_name}",
            "unit": "% resolved",
            "higher_is_better": True,
            "source_id": "swebench",
            "entries": []
        }

        for item in results:
            # From SWE-bench schema: name, resolved, date, logs, trajs, site, verified, oss, warning...
            model = item.get("name") or "Unknown Model"
            score = safe_float(item.get("resolved"))
            date = item.get("date")

            # skip warnings and missing scores
            if item.get("warning"):
                continue
            if score is None:
                continue

            bench["entries"].append({
                "model": model,
                "score": score,
                "date": date,
                "meta": {
                    "logs": item.get("logs"),
                    "trajs": item.get("trajs"),
                    "site": item.get("site"),
                    "verified": item.get("verified"),
                    "oss": item.get("oss"),
                    "folder": item.get("folder"),
                    "org_logo": item.get("org_logo"),
                }
            })

        out["benchmarks"].append(bench)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    total = sum(len(b["entries"]) for b in out["benchmarks"])
    print(f"[OK] Wrote {len(out['benchmarks'])} benchmarks / {total} rows -> {OUTPUT}")


if __name__ == "__main__":
    main()
