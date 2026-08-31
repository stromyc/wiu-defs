#!/usr/bin/env python3
"""Prove or refute a wayside's field ORDER from captured packets.

The auto-generated defs are signal-first (switches last); OUR CN capture analysis
proved the true order is switch-first. This tool tests that per WIUID *from data*
rather than assuming, using the same framing-slip discriminator the CN report used:

  A switch field only ever legitimately reads 1 (Reverse) or 2 (Normal). It reads
  0 (Invalid) or 3 (out-of-correspondence) essentially never in steady state — and
  a MIS-ALIGNED template (wrong order) sprays the "switch" bits across signal data,
  producing lots of 0/3. So: decode every captured frame under each candidate
  ordering and score by the fraction of frames whose switch field(s) are all in
  {1,2}. The ordering that keeps the switch valid is the real one.

Usage:
    python3 scripts/analyze_cp_order.py CAPTURE.jsonl [more.jsonl[.gz] ...]
    python3 scripts/analyze_cp_order.py --only 710597729310 caps/*.jsonl*

Captures are the resolved WIU stream (one JSON object per line with a WIUID and a
hex `data` field — e.g. rpi/data/captures/wiu_*.jsonl[.gz], or anything the
aggregator emits). This changes NO defs; it only reports what the data supports.
"""
import argparse
import glob
import gzip
import json
import os
import sys
from collections import defaultdict

FIELD_WIDTHS = {"signal": 5, "switch": 2}
VALID_SWITCH = {1, 2}


def hex_to_bits(data_hex):
    data_hex = str(data_hex).replace(" ", "")
    if not data_hex:
        return []
    nbits = len(data_hex) * 4
    val = int(data_hex, 16)
    return [(val >> (nbits - 1 - i)) & 1 for i in range(nbits)]


def take(bits, off, w):
    return sum(b << i for i, b in enumerate(bits[off:off + w]))


def decode(bits, kinds):
    """Return (switch_values, overran) for a kinds list like ['switch','signal',...]."""
    off, sw = 0, []
    for k in kinds:
        w = FIELD_WIDTHS[k]
        if off + w > len(bits):
            return sw, True
        if k == "switch":
            sw.append(take(bits, off, w))
        off += w
    return sw, False


def candidates(kinds):
    """current (as stored) and switch-first (all switches, then all signals)."""
    sw = [k for k in kinds if k == "switch"]
    sig = [k for k in kinds if k == "signal"]
    return {"current": list(kinds), "switch_first": sw + sig}


def open_any(p):
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("captures", nargs="+")
    ap.add_argument("--only", help="single WIUID to test")
    ap.add_argument("--min-frames", type=int, default=10)
    ap.add_argument("--wius", default=os.path.join(os.path.dirname(__file__), "..", "wius"))
    args = ap.parse_args()

    # current ind (kinds) per WIUID. Accepts both the repo's flat wius/ and the
    # ITC-STACK config/shared/wius/<sub>/ layout; only <digits>.json are read.
    import re
    kinds_of = {}
    for f in glob.glob(os.path.join(args.wius, "**", "*.json"), recursive=True):
        if not re.fullmatch(r"\d+\.json", os.path.basename(f)):
            continue
        for wid, e in json.load(open(f)).get("waysides", {}).items():
            kinds_of[str(wid)] = [next(iter(s)) for s in e.get("ind", []) if s]

    # gather frames
    frames = defaultdict(list)
    files = [p for pat in args.captures for p in glob.glob(pat)]
    for path in files:
        try:
            for line in open_any(path):
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                wid = str(o.get("WIUID") or o.get("wiuid") or "")
                data = o.get("data")
                if wid and data and (not args.only or wid == args.only):
                    frames[wid].append(data)
        except OSError as e:
            print(f"warn: {path}: {e}", file=sys.stderr)

    print(f"{len(files)} capture file(s); {sum(len(v) for v in frames)} frames for "
          f"{len(frames)} WIUIDs\n")
    hdr = f"{'WIUID':13} {'frames':>6}  {'current':>18}  {'switch_first':>18}  verdict"
    print(hdr); print("-" * len(hdr))

    for wid in sorted(frames):
        fr = frames[wid]
        if len(fr) < args.min_frames or wid not in kinds_of or "switch" not in kinds_of[wid]:
            continue
        bitsets = [hex_to_bits(d) for d in fr]
        scores = {}
        for name, kinds in candidates(kinds_of[wid]).items():
            good = tot = 0
            for bits in bitsets:
                sw, over = decode(bits, kinds)
                if over or not sw:
                    continue
                tot += 1
                if all(v in VALID_SWITCH for v in sw):
                    good += 1
            scores[name] = (good, tot)

        def pct(t):
            g, n = t
            return f"{(100*g/n):5.1f}% ({g}/{n})" if n else "   n/a"

        cur, swf = scores["current"], scores["switch_first"]
        cur_p = (cur[0] / cur[1]) if cur[1] else -1
        swf_p = (swf[0] / swf[1]) if swf[1] else -1
        cand = candidates(kinds_of[wid])
        if cand["current"] == cand["switch_first"]:
            verdict = "(switch already first)"
        elif max(cur_p, swf_p) < 0.5:
            verdict = "SWITCH INVALID BOTH WAYS -> likely mistyped (no real switch)"
        elif swf_p > cur_p + 0.05:
            verdict = "SWITCH-FIRST (reversed)"
        elif cur_p >= swf_p:
            verdict = "current OK"
        else:
            verdict = "inconclusive"
        print(f"{wid:13} {len(fr):6}  {pct(cur):>18}  {pct(swf):>18}  {verdict}")

    print("\nA clean 'SWITCH-FIRST (reversed)' means: current template sprays the switch "
          "bits (low valid%), switch-first keeps it valid. Then re-order that def and lock "
          "it with samples/<wiuid>.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
