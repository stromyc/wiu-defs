# Cleared-route logic (CTC strip green tracing)

Authoritative spec for when the dispatcher board paints a **green cleared route**
through a signal. Validated by Chris (signal domain). Implemented in
`LiveTrainTracking/services/ctcRouteTracer.js`.

## Aspect classes

| class  | aspects | meaning |
|--------|---------|---------|
| STOP   | Stop (15) | no movement |
| RESTR  | Restricting (incl. CN value 14, red-over-lunar) | restricted speed — a route BOUNDARY, never itself a cleared route |
| APPR   | Approach / Advance Approach / Diverging Approach | proceed, restriction ahead |
| CLEAR  | Clear | proceed, nothing ahead |

RESTR is identified by the **red-over-lunar head**, not the name — CN value 14 is
tabled `proposed="Flashing Yellow (?)"` but `i2a="Restricting-class"` with a
red/lunar mast, so the head signature is authoritative.

## Truth table — automatic intermediate

Evaluated per intermediate, per frame, from its two signals (N = northbound-
governing, S = southbound-governing).

```
                       SOUTHBOUND signal
                    STOP    RESTR   APPR    CLEAR
                 +-------+-------+-------+-------+
   NORTH  STOP   |   -   |   -   |  SB   |  SB   |
   BOUND  RESTR  |   -   |   -   |  SB   |  SB   |
  signal  APPR   |  NB   |  NB   |   -   |   -   |
          CLEAR  |  NB   |  NB   |   -   |   -   |
                 +-------+-------+-------+-------+
     NB = green northbound   SB = green southbound   - = no route (resting)
```

## Rule

```
green in direction D  IFF  signal_D is a proceed (APPR or CLEAR)
                      AND  opposite signal is STOP or RESTRICTING
```

A cleared route is **directional**: it exists only when the opposing direction is
knocked down. A **proceed both ways** (any mix of APPR/CLEAR in both directions)
is the **RESTING state** — never a cleared route, and never "cleared both ways."

## Control points are exempt

A control point is dispatcher-controlled: a proceed aspect there **is** a lined
route, so it seeds a cleared route regardless of the opposite head. The rule above
applies only to automatic intermediates.

## Moving trains ("knocking down behind")

The table is per-frame; movement is the sequence of frames. As a train advances,
aspects change and the green re-evaluates:

- **Ahead** of the train: proceed with the opposing direction locked out (APB
  tumbledown) → green in the direction of travel.
- **The occupied block**: both protecting signals at Stop → shows as **occupancy
  (red)**, not green.
- **Behind** the train, as it clears: the vacated block's opposing head returns to
  Clear while the travel direction may still read Approach — a **proceed-both-ways
  resting/clearing state**, so no green. Direction is conveyed by the green route
  itself, not by a separate occupancy arrow.

## Occupancy note

`occ` value is GEOGRAPHIC (N-end / S-end / both), not directional. A block is
reported by BOTH bounding waysides (north one as S-end, south one as N-end), so a
per-value arrow is meaningless — direction is a TRANSITION (which end lit first)
and belongs to the stateful movement tracker. The board lights occupied blocks
plainly; the green cleared route shows the movement's direction.
