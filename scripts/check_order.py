#!/usr/bin/env python3
"""Field-order sanity check (ours, on top of Todd's structural validate.py).

Flags decode-order problems the schema can't see:

  * a SWITCHED WIU whose switch is not field 0 — the auto-generator emitted
    signal-first templates, but OUR capture analysis (docs/findings/signal-order-*)
    proved the true CN order is switch-first `[SW][SIG1][SIG2][SIG3]`. A switch in
    a later field means the bit offsets are almost certainly reversed.
  * `[signal, switch]` — a 1-signal + 1-switch shape that is often a 2-signal
    intermediate whose second head was mis-typed as a switch (byte slip).

By default this WARNS and exits 0 (there is a known backlog — see
docs/DISCREPANCIES.md). Run with --strict to fail CI once the backlog is cleared,
so no NEW reversed template can slip in.
"""
import argparse
import glob
import json
import os
import sys


def kinds(entry):
    return [next(iter(s)) for s in entry.get("ind", []) if s]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="exit nonzero if any finding")
    ap.add_argument("root", nargs="?", default=os.path.join(os.path.dirname(__file__), "..", "wius"))
    args = ap.parse_args()

    reversed_hits, byteslip_hits = [], []
    for f in sorted(glob.glob(os.path.join(args.root, "*.json"))):
        for wid, entry in json.load(open(f)).get("waysides", {}).items():
            k = kinds(entry)
            if "switch" not in k:
                continue
            if k == ["signal", "switch"]:
                byteslip_hits.append((wid, entry.get("name") or "", k, os.path.basename(f)))
            elif k[0] != "switch":                       # switch present but not first
                reversed_hits.append((wid, entry.get("name") or "", k, os.path.basename(f)))

    def show(title, hits):
        print(f"\n{title}: {len(hits)}")
        for wid, name, k, fn in sorted(hits):
            print(f"  {wid}  {name:22} {k}   ({fn})")

    show("SWITCH-NOT-FIELD-0 (likely reversed order)", reversed_hits)
    show("[signal, switch] (possible intermediate byte-slip)", byteslip_hits)

    total = len(reversed_hits) + len(byteslip_hits)
    print(f"\ncheck_order: {total} finding(s). See docs/DISCREPANCIES.md; prove/fix with scripts/analyze_cp_order.py.")
    return 1 if (args.strict and total) else 0


if __name__ == "__main__":
    sys.exit(main())
