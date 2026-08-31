#!/usr/bin/env python3
"""Solve a CN wayside's true field layout from captures using the ASPECT vocabulary.

Stronger than switch-validity alone: a real signal field decodes to a KNOWN CN
aspect (3/7/8/14/15/17/18); a field mis-typed as a switch, or a dropped/truncated
field, will not. For each wayside we score every candidate layout by the fraction
of frames in which EVERY field is sensible (signals->known aspect, switches->1/2),
and pick the FULLEST layout that holds >=85%. Known-good defs score ~100% and are
left alone; truncated/mistyped ones surface a better-fitting layout.

Usage:
    python3 scripts/cn_solve.py <wius_dir> <capture.jsonl[.gz] ...>

Limitation: only tries 0- or 1-switch layouts, so genuine multi-switch plants
(e.g. [switch,switch,sig,sig,sig,sig]) score their CURRENT layout high and show a
bogus low best-fit — treat a high cur%% as already-correct. Changes NO defs.
"""

import json,gzip,glob,sys,re
from collections import defaultdict
FW={"signal":5,"switch":2}
CN_OK={3,7,8,14,15,17,18}     # known CN aspects (÷ candidate 14)
SW_OK={1,2}
def bits(h):
    h=str(h).replace(" ","");n=len(h)*4
    if not h:return[]
    v=int(h,16);return[(v>>(n-1-i))&1 for i in range(n)]
def openany(p): return gzip.open(p,'rt') if p.endswith('.gz') else open(p)
wroot=sys.argv[1]; caps=sys.argv[2:]
kinds_of={}
for f in glob.glob(wroot+"/**/*.json",recursive=True):
    if not re.fullmatch(r"\d+\.json",f.split("/")[-1]):continue
    for wid,e in json.load(open(f)).get("waysides",{}).items():
        kinds_of[str(wid)]=[next(iter(s)) for s in e.get("ind",[]) if s]
frames=defaultdict(list)
for pat in caps:
    for p in glob.glob(pat):
        try:
            for ln in openany(p):
                ln=ln.strip()
                if not ln:continue
                try:o=json.loads(ln)
                except:continue
                w=str(o.get("WIUID")or o.get("wiuid")or"");d=o.get("data")
                if w.startswith("710343")and d:frames[w].append(str(d).replace(" ",""))
        except OSError:pass
def score(bitsets,struct):
    good=tot=0
    for b in bitsets:
        off=0;ok=True;fits=True
        for k in struct:
            if off+FW[k]>len(b):fits=False;break
            v=sum(bit<<i for i,bit in enumerate(b[off:off+FW[k]]))
            if k=="signal" and v not in CN_OK: ok=False
            if k=="switch" and v not in SW_OK: ok=False
            off+=FW[k]
        if not fits:continue
        tot+=1; good+=ok
    return (good/tot if tot else 0),tot
def candidates(maxbits):
    out=[]
    for nsw in(0,1):
        for nsig in range(1,7):
            st=["switch"]*nsw+["signal"]*nsig
            if sum(FW[x] for x in st)<=maxbits: out.append(st)
    return out
print(f"{'WIUID':13} {'current':24}{'cur%':>5}   best-fit (sensible%, N)")
print("-"*92)
for w in sorted(frames):
    k=kinds_of.get(w);fr=frames[w]
    if not k or len(fr)<20:continue
    bs=[bits(h) for h in fr]
    mb=max(len(b) for b in bs)
    curp,_=score(bs,k)
    cand=[]
    for st in candidates(mb):
        p,n=score(bs,st)
        cand.append((p,sum(FW[x] for x in st),st,n))
    # pick fullest structure with sensible% >= .85 (fall back to max %)
    good=[c for c in cand if c[0]>=0.85]
    pick=max(good,key=lambda c:(c[1],c[0])) if good else max(cand,key=lambda c:c[0])
    star="" if pick[2]==k else "  <-- CHANGE"
    print(f"{w:13} {' '.join(k):24}{curp*100:4.0f}%   {' '.join(pick[2]):28}({pick[0]*100:3.0f}%, {pick[3]}){star}")
