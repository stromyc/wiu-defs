# Golden decode samples

One file per WIUID whose field order you want to lock down. `scripts/selftest.py`
decodes `data` against that wayside's `ind` and asserts it matches `expected` —
so a wrong `ind` order (the CN‑vs‑CPKC problem) fails CI instead of silently
mis‑decoding on air.

```
samples/<wiuid>.json
{
  "wiuid": "710343550505",
  "data":  "02 04 05 00 00 00",        // raw datagram user data (hex), as captured
  "note":  "capture 2026-08-.., field-observed N=Clear S=Stop",
  "expected": [                         // decoded fields, IN ORDER
    { "kind": "signal", "label": "N", "value": 5 },
    { "kind": "signal", "label": "S", "value": 0 }
  ]
}
```

- `data` + `expected` must come from a **real capture cross‑checked against a
  field observation** — not from the current decode (that would just assert the
  bug is the bug).
- Assert on `value` (the raw decoded bits), not aspect names — that's what pins
  the field ORDER and is railroad‑independent.
- Add one per railroad at minimum; more for any plant whose order you're unsure of.
