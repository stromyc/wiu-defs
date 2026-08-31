# Decode discrepancies to resolve

Field-order / field-kind problems in the defs, most auto-generated. The
authority is OUR capture-based analysis (docs/findings/signal-order-*), NOT
assumed order. Fix each with `scripts/analyze_cp_order.py` proof, then lock it
with a `samples/<wiuid>.json` golden test before committing.

Validated-good baseline: CN switched CPs `[SW][SIG1=lone][SIG2=normal][SIG3=reverse]`.


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
