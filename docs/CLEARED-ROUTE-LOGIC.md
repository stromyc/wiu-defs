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

---

# Switched control points — WHICH RAIL the green runs (main vs siding)

The intermediate rule above answers *is there a route, and which direction*. A
switched control point adds a second question: **does the route run the main or
divert onto the siding?** The answer is read from the HEADS, never a switch field.

## Canonical field order (ITC-STACK/TECH-DOCS/CN_SWITCHED_WIU_SIGNAL_FIELD_ORDER)

A one-switch / three-signal WIU serializes:

```
    [ SWITCH ][ LONE ][ NORMAL ][ REVERSE ]
       2 bits    5b       5b        5b
                  |         |         |
                  |         |         +-- REVERSE-route head  (R-suffix: NR / SR)
                  |         +------------ NORMAL-route head   (N-suffix: NN / SN)
                  +---------------------- LONE point-side head (single char: N / S)
```

Compass names follow plant orientation (NOT invariant):
`lone N -> heads SN/SR` · `lone S -> heads NN/NR`.

## The gating that tells you the rail

NORMAL and REVERSE heads are COMPLEMENTARY — the switch can only be one way:

```
                 SW = NORMAL      SW = REVERSE
   NORMAL head     PROCEED           STOP           <- N-suffix (NN/SN)
   REVERSE head     STOP            PROCEED          <- R-suffix (NR/SR)
   LONE head      may govern either; may show a diverging aspect under reverse
```

So the rule is:

```
   route runs the SIDING  IFF  the REVERSE head (R-suffix) shows a PROCEED
   otherwise it runs the MAIN
```

Do NOT read the switch field for this. The decoder ships a numeric switch `value`,
never a `position` string — the old `switchOf()` read `position` and so never
fired, and every reverse route wrongly rendered on the main. The proceeding
reverse head IS the reverse lining. (`reverseHeadProceeds()` in ctcRouteTracer.js.)

## ASCII — normal vs reverse at one plant

Strip convention: NORTH = left, SOUTH = right (milepost decreases rightward).
Plant below has lone S (point end, right) and frog heads NN/NR (left); siding below.
`●` = proceed, `○` = Stop. `═` main, `─` siding, green route drawn as `▓`.

```
NORMAL lined (NN ●, NR ○) — northbound green stays on the MAIN:

        NN●                                   S○
   ▓▓▓▓▓▓|▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓●═══════o──|═══   MAIN   ── northbound ▓ →
                       ╲
        NR○             ╲______________________________  siding (white, unused)


REVERSE lined (NN ○, NR ●) — northbound green DIVERTS to the SIDING:

        NN○                                   S○
   ═══════|═══════════════╲══════════════════o──|═══   MAIN (white past the points)
                           ╲(points)
        NR●                 ╲
   ▓▓▓▓▓▓|▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓●═══════════════════════   SIDING   ── northbound ▓ →
```

The green ALWAYS diverges on the turnout/partner side and follows the same path as
the white siding rail — the exact leg direction (up/down, which end) per plant is
in ITC-STACK/TECH-DOCS/{NW_L,NW_R,SE_L,SE_R}_Turnout.

---

# The route walk (how far the green extends)

Ported in `ctcRouteTracer.js`. From every head showing a proceed (seed), step
plant-to-plant in the head's compass direction:

1. **Seed** at a clear-proceed head (CLEAR/APPR, never RESTR/STOP). Intermediates
   also require the opposite head knocked down (the resting-state rule above); CPs
   are exempt.
2. **Rail** for each hop = `reverseHeadProceeds(plant)` — siding if the plant's
   R-suffix head proceeds, else main.
3. **Continue** to the next plant as long as ANY facing head still clear-proceeds.
   > CRITICAL: do NOT stop on the un-lined complementary head. A reversed plant
   > parks NN at Stop while NR proceeds down the siding — stopping on NN would end
   > the route on the main and (in a meet) draw a head-on. Continue on the head
   > that IS lined.
4. **Terminate** at: the governing head showing STOP or RESTRICTING (the boundary),
   an OCCUPIED block ahead (red wins), an UNHEARD wayside (never assert unseen
   track), or the corridor end (emit an open stub).

---

# Worked example — a MEET at Midway (two trains, two rails)

Northbound holds in the siding; southbound takes the main. Both are cleared routes;
they must render on DIFFERENT rails, never as two arrows converging on the main.

Midway's siding is BELOW the main (SIDINGS side:"below").

```
        N Midway                                         S Midway
          NN○                                              SN●
   ══════════●═══════════════════ MAIN ═══════════════════════●══════   ◀▓  SOUTHBOUND (main → SN)
              ╲                                             ╱
          NR● ╲______________________ SIDING _____________╱  SR○
   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (below the main) ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓        ▓▶ NORTHBOUND (siding, holds at N Midway NR)

   NORTHBOUND  ▓  seeds where its REVERSE head proceeds, diverts DOWN to the siding,
               runs it north, terminates at N Midway NR (restricting = hold).
   SOUTHBOUND  ◀▓ seeds on the main, runs south, terminates at S Midway SN.
```

- Northbound rail = siding because a REVERSE head proceeds at its switched plant.
- Southbound rail = main because its NORMAL head proceeds.
- The two greens never share a rail → a meet, not a collision. If you ever see the
  two arrows on the SAME horizontal main, the rail read (step 2) or the "don't stop
  on the un-lined head" continue (step 3) has regressed.

*(Exact head compass names per plant depend on orientation — lone N vs lone S —
so confirm NR vs SR against the plant's own labels; the LOGIC is rail-by-reverse-
head regardless of the compass name.)*
