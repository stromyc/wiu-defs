# Occupancy field (`occ`) — CONFIRMED mapping, 21 CN waysides live

2-bit track circuit after the signals: `used=10` → occ at [10:12] (2-signal),
`used=17` → [17:19] (switch+3sig). Value = bit0 + 2*bit1 (LSB-first in field),
bits MSB-first across payload. Fixtures (MUST hold): `761F`→2, `C3AF`→1.

## Value → state (CONFIRMED against SB+NB frames by the capture side)
| value | bits | state (GEOGRAPHIC — never directional) |
|---|---|---|
| 3 | (1,1) | Clear (both sub-circuits unoccupied) |
| 2 | (0,1) | N-end occupied |
| 1 | (1,0) | S-end occupied |
| 0 | (0,0) | Both occupied |

Direction lives in the TRANSITION out of 3, not the value:
`3→2 = SOUTHBOUND` (enters north end first), `3→1 = NORTHBOUND`.

## Deployment hazards (from the capture side — honor all)
1. Name states geographically (CLEAR/N_END/S_END/BOTH). Direction is a transition,
   computed downstream — do NOT bake it into the state.
2. **Bit order is NOT universal.** S Duplainville (557505) is inverted (b17=south,
   b18=north) per SDUP-OCCUPANCY-20260830 §5 — DEFERRED from this batch until its
   fixtures are in hand.
3. **Dead field reads as permanently occupied.** N Sussex (565005) carries the field
   structurally but never populates it — sits at value 0 forever (NSUSSEX-OCCUPANCY-
   20260826). Gate on liveness: a live field rests at 3 most of the time and shows
   full cycles. Our enum already excluded dead fields, so the 21 here are all live.
4. Bracket rule: onset is first-OBSERVED at a frame; true transition lies back to the
   previous frame (4850 brackets 24–820 s). Timestamp the observation, not the event.

## Status
- 21 CN waysides carry `occ` (557505 deferred). selftest 18/18 (occ=2 + prefix match).
- Decoder: FIELD_WIDTHS["occ"]=2 + OCC_STATES + annotate branch (occupancy state only;
  direction is a stateful fast-follow). Applied to EC2 /home/ubuntu/wiu_decode.py.
- `occ` is the LAST field, so unpatched decoders decode all signals and skip occ —
  backward-compatible fleet-wide.
- TODO: direction logic (per-WIUID transition tracking); re-enable 557505 (needs
  fixtures); patch Pi decoders; React board occupancy indicator (layer 3).
