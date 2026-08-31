# Decode discrepancies to resolve

Field-order / field-kind problems in the defs, most auto-generated. The
authority is OUR capture-based analysis (docs/findings/signal-order-*), NOT
assumed order. Fix each with `scripts/analyze_cp_order.py` proof, then lock it
with a `samples/<wiuid>.json` golden test before committing.

Validated-good baseline: CN switched CPs `[SW][SIG1=lone][SIG2=normal][SIG3=reverse]`.


## RESOLVED — CN batch 1 (2026-08-30, data-gated; 15 waysides)

Method: `scripts/cn_solve` scores every candidate field layout by the fraction of
captured frames in which EVERY field is *sensible* — signals decode to a known CN
aspect (3/7/8/14/15/17/18), switches read Normal/Reverse. The fullest layout that
holds ≥95% is the true one. This supersedes the earlier switch-validity-only pass,
which mis-sized three defs. Calibration: all known-good defs (542005, 546005,
543505, 549505…) score 98–100% and are left untouched. Each fix locked with
`samples/<wiuid>.json` decoding to real aspects.

Switch-first CP, signals had been dropped/truncated → `[switch,sig,sig,sig]`:
- **710343526505**, **535505**, **539505**, **549005** (were `[switch]` only — 22 bits of signal dropped)
- **710343537005** (was `[sig,switch]`), **585505** (was `[sig,switch]`)
- **710343534505** (was `[sig,switch]`) — proven by a Reverse+`Approach Diverging` diverging move

Two signals, phantom switch removed → `[sig,sig]`:
- **710343530005** (was `[sig,sig,switch]`; earlier mis-fixed to switch-first — corrected: it is two signals `Restricting/Approach`)
- **710343527505** (was `[sig,switch]`, switch read Idle/unknown)
- **710343530006, 533005, 533006, 539005, 548005, 577005** (were `[sig,switch]`/`[sig,sig,switch]`)

Held for field confirmation:
- **710343534005** `[switch,switch]` — reads two *valid* switches (100%); no signal layout fits (≤12%).
  Data cannot refute it; needs the physical plant's head/switch count.

Still open: aspect-name (label) cross-check against a physical observation.

## A. REVERSED switched-CP suspects — switch present but NOT field 0, ≥2 signals. Likely auto-gen put switches last; validate switch-first per capture.  (29)

- **[CN] 710343530005** : `['signal', 'signal', 'switch']`
- **[CN] 710343530006** : `['signal', 'signal', 'switch']`
- **[CN] 710343539005** : `['signal', 'signal', 'switch']`
- **[CN] 710343548005** : `['signal', 'signal', 'switch']`
- **[CP] 710597639010** : `['signal', 'signal', 'signal', 'switch']`
- **[CP] 710597639710** : `['signal', 'signal', 'signal', 'switch']`
- **[CP] 710597729310** : `['signal', 'switch', 'switch']`
- **[CP] 710597730410** W of Duplainville (twd Pewaukee): `['signal', 'signal', 'signal', 'switch']`
- **[CP] 710597731210** : `['signal', 'signal', 'switch']`
- **[CP] 710597731410** : `['signal', 'signal', 'signal', 'switch']`
- **[CP] 710597731910** : `['signal', 'signal', 'signal', 'switch']`
- **[CP] 710597732110** Cooney E: `['signal', 'signal', 'signal', 'switch']`
- **[CP] 710597733710** : `['signal', 'switch', 'switch']`
- **[CP] 710597733713** : `['signal', 'switch', 'switch']`
- **[CP] 710597734710** : `['signal', 'switch', 'switch']`
- **[CP] 710597736110** : `['signal', 'switch', 'switch']`
- **[CP] 710597737710** : `['signal', 'signal', 'signal', 'signal', 'signal', 'signal', 'signal', 'switch', 'switch', 'switch', 'switch', 'switch', 'switch', 'switch']`
- **[CP] 710598023410** : `['signal', 'signal', 'signal', 'switch']`
- **[CP] 710598024210** : `['signal', 'signal', 'signal', 'signal', 'signal', 'switch', 'switch', 'switch', 'switch', 'switch']`
- **[CP] 710598024410** : `['signal', 'signal', 'signal', 'switch']`
- **[CP] 710598024413** : `['signal', 'switch', 'switch']`
- **[CP] 710598024810** : `['signal', 'signal', 'signal', 'signal', 'switch', 'switch']`
- **[CP] 710598026210** : `['signal', 'signal', 'signal', 'signal', 'signal', 'switch', 'switch', 'switch', 'switch', 'switch']`
- **[CP] 710598027010** : `['signal', 'signal', 'signal', 'signal', 'switch', 'switch', 'switch', 'switch']`
- **[CP] 710598027613** : `['signal', 'signal', 'signal', 'switch']`
- **[CP] 710598027710** : `['signal', 'signal', 'signal', 'signal', 'signal', 'signal', 'switch', 'switch', 'switch', 'switch', 'switch', 'switch']`
- **[CP] 710598027910** : `['signal', 'switch', 'switch']`
- **[CP] 710598028410** : `['signal', 'signal', 'signal', 'signal', 'signal', 'signal', 'switch', 'switch', 'switch', 'switch']`
- **[CP] 710598028510** : `['signal', 'signal', 'signal', 'switch', 'switch']`

## B. Byte-slip / mis-typed intermediate suspects — `[signal, switch]`. May be a 2-signal intermediate whose 2nd head was typed as a switch (2 bits read where 5 belong).  (18)

- **[CN] 710343527505** : `['signal', 'switch']`
- **[CN] 710343533005** : `['signal', 'switch']`
- **[CN] 710343533006** : `['signal', 'switch']`
- **[CN] 710343534505** : `['signal', 'switch']`
- **[CN] 710343537005** : `['signal', 'switch']`
- **[CN] 710343568325** : `['signal', 'switch']`
- **[CN] 710343577005** : `['signal', 'switch']`
- **[CN] 710343585505** : `['signal', 'switch']`
- **[CP] 710597639310** : `['signal', 'switch']`
- **[CP] 710597639510** : `['signal', 'switch']`
- **[CP] 710597640510** : `['signal', 'switch']`
- **[CP] 710597729510** : `['signal', 'switch']`
- **[CP] 710597729513** : `['signal', 'switch']`
- **[CP] 710597729810** : `['signal', 'switch']`
- **[CP] 710597730610** : `['signal', 'switch']`
- **[CP] 710598022621** : `['signal', 'switch']`
- **[CP] 710598026413** : `['signal', 'switch']`
- **[CP] 710598026713** : `['signal', 'switch']`

## C. Three signals, no switch — unusual; verify field count against a capture.  (2)

- **[CN] 710343550505** : `['signal', 'signal', 'signal']`
- **[CP] 710597730213** : `['signal', 'signal', 'signal']`

## D. Other signals-only shapes to eyeball.  (2)

- **[CP] 710597730210** : `['signal', 'signal', 'signal', 'signal']`
- **[CP] 710598023810** : `['signal']`

## OK — switch is field 0 (matches the validated CN order). Left for reference.  (14)

_14 waysides — not listed individually._

## OK — 2-signal intermediate.  (38)

_38 waysides — not listed individually._

## OK-ish — switch-only WIU (no signal order to get wrong).  (15)

_15 waysides — not listed individually._
