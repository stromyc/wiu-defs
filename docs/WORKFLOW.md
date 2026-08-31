# wiu-defs — single source of truth across the fleet

`github.com/stromyc/wiu-defs` is the ONE canonical home for WIU field definitions
(names + `ind` decode structure) for every railroad. Every machine clones it; nobody
edits WIU defs anywhere else.

## Topology

| Machine | Clone path | Decoder reads | Role |
|---|---|---|---|
| Mac Studio | `~/Development/wiu-defs` | — | authoring / analysis |
| AWS EC2 (`ec2-ltt`) | `/home/ubuntu/wiu-defs` | `--defs /home/ubuntu/wiu-defs/wius` (pm2 `itc-decode`) | **feeds the website** |
| rpi5-ptc `100.80.196.94` | `~/wiu-defs` | `--defs ~/wiu-defs/wius/*.json` (user svc `itc-decode`) | field receiver + local monitor |
| rpi5-util `100.76.193.57` | `~/wiu-defs` | `--defs ~/wiu-defs/wius/*.json` (user svc `itc-decode`) | field receiver + local monitor |
| ThinkPad / future | `~/wiu-defs` | point its decoder `--defs` at the clone | onboard per below |

The Pis and the ThinkPad **push raw frames to the EC2 aggregator**; they do not decode
for the website. Only EC2's decode reaches livetraintracking.com.

## Daily workflow

**Make a change (analysis on any machine):**
```bash
cd <clone>                 # ~/wiu-defs (Pi/EC2) or ~/Development/wiu-defs (Mac)
git pull                   # start from latest
# ...edit wius/*.json (or run analysis that writes them)...
python3 scripts/selftest.py    # decode-correctness gate (must pass)
git add -A && git commit -m "..." && git push
```

**Pick up others' changes (any machine):**
```bash
cd <clone> && git pull
# restart that machine's decoder so it reloads defs:
#   EC2:  pm2 restart itc-decode
#   Pi:   systemctl --user restart itc-decode.service
```

Defs load at decoder **startup only** — a pull changes nothing until the restart.
On EC2 that restart is what makes a change live on the website.

## Website deploy (EC2), end to end

```bash
ssh ec2-ltt
cd /home/ubuntu/wiu-defs && git pull                 # decode defs (names + ind)
pm2 restart itc-decode                               # make decode live
# board identity/inventory (separate repo — see below):
cd /home/ubuntu/liveTrainTracking/LiveTrainTracking && git pull
node scripts/buildItcMap.js --wius /home/ubuntu/wiu-defs/wius --out config/itcMap.json
# (itcMap.json is read per-request; no app restart needed)
```

`itcMap.json` = the board's inventory + display names + geography + aspect render
tables. It is GENERATED from `wiu-defs` (names + ind) + `config/itcMap.overlay.json`
(milepost/side/cpId/kind) in the LiveTrainTracking repo. So a rename in `wiu-defs`
flows to the board through `buildItcMap.js`. See [[wiu-defs-repo-and-deploy]].

## Onboard a new machine (ThinkPad, future Pi)

```bash
ssh -T git@github.com                                # confirm the key authenticates as stromyc
git clone git@github.com:stromyc/wiu-defs.git ~/wiu-defs
# point that machine's decoder at the clone. For a systemd --user itc-decode.service,
# set ExecStart to read the clone via shell glob so new railroad files auto-include:
#   ExecStart=/bin/sh -c 'exec python3 -u <path>/wiu_decode.py --state state.json --quiet \
#             --defs /home/<user>/wiu-defs/wius/*.json'
# then: systemctl --user daemon-reload && systemctl --user restart itc-decode.service
```

## Notes / gotchas

- **Do not edit WIU defs in the `itc-stack` repo any more** (`config/shared/wius`).
  That embedded copy is why histories diverged on 2026-08-31. The decoder now reads
  `~/wiu-defs/wius`; the old copy is inert. Analysis scripts may still live in
  itc-stack but should read `~/wiu-defs/wius` as input.
- `wiu_decode.py` on the Pis opens each `--defs` entry as a file (no directory
  expansion), which is why the service uses a `*.json` shell glob. The EC2 build
  accepts a bare directory. Either way, point at the clone's `wius/`.
- Every commit must pass `scripts/selftest.py`. Structure changes should add a
  `samples/<wiuid>.json` golden test first.
