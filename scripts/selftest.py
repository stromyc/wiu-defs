#!/usr/bin/env python3
"""Decode-correctness gate for the WIU definitions.

Todd's validate.py checks STRUCTURE (schema, no duplicate WIUIDs). This checks
BEHAVIOUR: that a wayside's `ind` order actually decodes a captured packet to the
expected fields. That is the failure mode structure can't catch — a valid JSON
`ind` in the wrong order (the CN-vs-CPKC problem) produces wrong aspects, not a
schema error.

Add a golden sample per WIUID whose order you want to lock down:

  samples/<wiuid>.json
  {
    "wiuid": "710343550505",
    "data":  "02 04 05 00 00 00",          # the raw datagram user data (hex)
    "expected": [                            # decoded fields, in order
      {"kind": "signal", "label": "N", "value": 5},
      {"kind": "signal", "label": "S", "value": 0}
    ]
  }

`data` and `expected` come from a real capture cross-checked against a field
observation. CI runs this on every PR; run it on the box after `git pull` too.

NOTE: the bit-unpacking below is copied verbatim from ITC-STACK
app/decode/wiu_decode.py (FIELD_WIDTHS / hex_to_bits / take_field / decode_fields).
It MUST stay in step with that decoder — ideally both import one shared module
later; for now, if you change the packing there, mirror it here.
"""
import glob
import json
import os
import sys

FIELD_WIDTHS = {"signal": 5, "switch": 2, "occ": 2}


def hex_to_bits(data_hex):
    data_hex = data_hex.replace(" ", "")
    nbits = len(data_hex) * 4
    val = int(data_hex, 16) if data_hex else 0
    return [(val >> (nbits - 1 - i)) & 1 for i in range(nbits)]


def take_field(bits, offset, width):
    chunk = bits[offset:offset + width]
    return sum(b << i for i, b in enumerate(chunk))  # LSB-first within the field


def decode_fields(data_hex, ind):
    bits = hex_to_bits(data_hex)
    fields, offset = [], 0
    for slot in ind:
        if not slot:
            continue
        kind, label = next(iter(slot.items()))
        width = FIELD_WIDTHS.get(kind)
        if width is None or offset + width > len(bits):
            break
        fields.append({"kind": kind, "label": label or str(len(fields) + 1),
                       "value": take_field(bits, offset, width)})
        offset += width
    return fields


def load_waysides():
    root = os.path.join(os.path.dirname(__file__), "..", "wius")
    ways = {}
    for f in sorted(glob.glob(os.path.join(root, "*.json"))):
        for wid, entry in json.load(open(f)).get("waysides", {}).items():
            ways[wid] = entry
    return ways


def main():
    ways = load_waysides()
    samples = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "samples", "*.json")))
    if not samples:
        print("selftest: no samples yet (add samples/<wiuid>.json to lock down decode order)")
        return 0

    failures = 0
    for s in samples:
        spec = json.load(open(s))
        wid = str(spec["wiuid"])
        entry = ways.get(wid)
        if not entry:
            print(f"FAIL {os.path.basename(s)}: WIUID {wid} not in any wius/*.json")
            failures += 1
            continue
        got = decode_fields(spec["data"], entry.get("ind", []))
        want = [{"kind": e["kind"], "label": e["label"], "value": e["value"]} for e in spec["expected"]]
        got_min = [{"kind": g["kind"], "label": g["label"], "value": g["value"]} for g in got]
        if got_min[:len(want)] == want:
            print(f"ok   {wid}  ({entry.get('name') or entry.get('sig')})")
        else:
            print(f"FAIL {wid}: decoded {got_min}\n            expected {want}")
            failures += 1

    print(f"\nselftest: {len(samples) - failures}/{len(samples)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
