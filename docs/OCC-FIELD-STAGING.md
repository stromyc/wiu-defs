# Occupancy field (`occ`) — staged, NOT yet on main

Branch `occ-field`. Adds a 2-bit track-circuit field after the signals on every
wayside that carries one. Discovered/validated with the capture side (they
reconstructed movements from it directly). DO NOT merge to main or deploy until
BOTH: (a) the decoder supports `occ`, and (b) the ring mapping below is confirmed —
otherwise the fleet's `wiu_decode.py` breaks on an unknown field kind.

## Scope (this branch)
22 **CN** waysides only. `occ` sits immediately after the signal fields:
- 2-signal intermediates → `used=10`, occ at bits **[10:12]**
- switch + 3-signal CPs (526505, 537005, 557505) → `used=17`, occ at bits **[17:19]**

CP (13) and UP (6) also show a varying field there, but their defs are still
mistyped/truncated, so `[used:used+2]` lands on real signal/switch bits, NOT the
circuit. **CP/UP occ waits on the CP/UP def-fix batch** — do not add it blind.

## Value → state (STAGED — confirm against the capture side before finalizing)
`take_field` is LSB-first, so value = bit0 + 2*bit1:
| value | bits (b10,b11) | staged meaning |
|---|---|---|
| 3 | (1,1) | Clear / unoccupied |
| 2 | (0,1) | Occupied — north end |
| 0 | (0,0) | Occupied — full |
| 1 | (1,0) | Occupied — south end / tail |

Ring (capture side): `(1,1)→(0,1)→(0,0)→(1,0)→(1,1)` = north-end-first = **southbound**;
reverse = northbound. Direction comes from the state *sequence*, not one frame.
**Hold the names + direction logic until they confirm which of 0/1/2 is leading vs tail.**

## Decoder patch (wiu_decode.py — itc-stack, all machines; apply on confirm)
```python
FIELD_WIDTHS = {"signal": 5, "switch": 2, "occ": 2}
OCC_STATES = {3: "Clear", 2: "Occupied (N)", 0: "Occupied", 1: "Occupied (S)"}  # STAGED
# in the annotate/attach-names step, alongside signal/switch:
elif kind == "occ":
    f["occupancy"] = OCC_STATES.get(f["value"])
# direction: keep prev occ per WIUID; on a transition, N-end-first => "SB", else "NB"
```
Mirror `FIELD_WIDTHS["occ"]=2` into scripts/selftest.py (done on this branch) and any
other decoder copy (React lib/decode.js for layer 3).

## Deploy order (when ready)
1. Confirm ring mapping.
2. Apply decoder patch to `wiu_decode.py`, deploy to EC2 + Pis (itc-stack path).
3. Merge `occ-field` → main; fleet `git pull` + restart decoders.
4. Layer 3: React board occupancy indicator (separate, LiveTrainTracking repo).

Order matters: decoder must understand `occ` BEFORE the defs carrying it reach a
running decoder.
