# Decode discrepancies to resolve

Waysides where an upstream (Todd) def and our def disagree on field ORDER/count.
We keep OUR def until a capture + field observation settles it. Add a
`samples/<wiuid>.json` golden test to lock the winner, then update the def.

- **710343550505** Sunset Drive: todd `['signal', 'signal']` vs ours `['signal', 'signal', 'signal']` — needs capture
