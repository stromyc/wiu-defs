# Using this fork (private WIU‑defs master)

This repo is a **private mirror** of Todd Taylor's
`itcmon-wiu-configurations`, plus our own coverage and a decode‑correctness gate.
It is the single source of truth for the field layouts our EC2 decoder uses.

## What's ours vs. upstream

- **CN (`103435.json`)** — merged: Todd's authoritative entries/labels (`N`,`S`,
  `NR`,`SN`,…) win on overlap; our additional CN waysides kept. Improvements here
  are candidates to PR back to Todd.
- **CP / UP / UNK (`105*.json`, `802*.json`, `510303.json`, `630514.json`)** —
  ours; Todd's repo doesn't carry these. This is where the CPKC order work lives.
- **`scripts/selftest.py` + `samples/`** — ours; a golden‑sample gate on decode
  behaviour, on top of Todd's structural `validate.py`.

## Syncing Todd's improvements in

```bash
git remote add upstream https://github.com/ToddTaylor/itcmon-wiu-configurations.git   # once
git fetch upstream && git merge upstream/main      # pulls his CN updates; clean if we didn't reformat his files
```

## Contributing a fix back to Todd (optional)

A private repo can't open a PR directly. When you have a CN fix worth sending:
spin up a throwaway **public** fork of his repo, cherry‑pick just that content
change onto a branch off `upstream/main`, push, open the PR, delete after merge.

## The EC2 update loop (making a change actually take effect)

`wiu_decode` loads defs **at startup only** — editing a file changes nothing
until the decoder restarts. So:

```bash
cd ~/wiu-defs && git pull                 # (or rsync from your workstation)
python3 scripts/validate.py               # structure gate
python3 scripts/selftest.py               # decode-correctness gate
pm2 restart itc-decode                     # MANDATORY — this is what makes it live
```

The decoder is pointed at the flat dir with `--defs ~/wiu-defs/wius` (supported by
the wiu_decode flat‑layout patch). Todd's CI auto‑bumps each file's `version` on
merge — surface that on the dashboard as the "defs live" badge so you can *see*
which version the aggregator is decoding against.
