#!/usr/bin/env python3
# Usage: python3 scripts/cn_field_extent.py <wius_dir> <capture.jsonl[.gz] ...>
# Reads the CURRENT def's leading-switch count, then counts signal heads by bit
# behaviour. KEY RULE (Chris): a trailing 5-bit field is a real head only if it is
# ASPECT-dominant (Stop/Clear/...); a field that sits at 0 ~99% of the time, is
# all-ones (31), or constant-0 is PADDING. Live vs dark doesn't matter -- a
# permanently-red head reads a constant 15 and is still a head. This does NOT infer
# switch-first reordering (it trusts the current switch positions); use cn_solve for
# order. Changes no defs.
# Field-extent by bit behaviour, dark-head aware:
#  signal head = 5-bit field with MSB(v>=16) set in <25% of frames AND not constant-0
#                (a permanently-red head is constant-15, MSB=0 -> still a head)
#  padding     = MSB set >=25% (all-ones tail) OR constant-0
#  switch      = leading 2-bit field reading {1,2} in >=80% of frames
import json,gzip,glob,sys,re
from collections import defaultdict,Counter
def bits(h):
    h=str(h).replace(" ","");n=len(h)*4;v=int(h,16) if h else 0
    return [(v>>(n-1-i))&1 for i in range(n)]
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
                if w.startswith("710343") and d: frames[w].append(bits(str(d)))
        except OSError:pass
def val(r,o,w): return sum(b<<i for i,b in enumerate(r[o:o+w]))
def infer(rows,curkinds):
    nb=max(len(r) for r in rows); off=0; out=[]
    # leading switches: use current def's leading-switch count if those fields read 1/2 well
    nlead=0
    for k in curkinds:
        if k!="switch": break
        nlead+=1
    for _ in range(nlead):
        if off+2>nb: break
        sw=[val(r,off,2) for r in rows if len(r)>=off+2]
        if sum(v in(1,2) for v in sw)/len(sw)>=0.80: out.append("sw"); off+=2
        else: break
    # then signals until padding
    while off+5<=nb:
        vals=[val(r,off,5) for r in rows if len(r)>=off+5]
        msb=sum(v>=16 for v in vals)/len(vals)
        distinct=len(set(vals))
        const0 = distinct==1 and vals[0]==0
        if msb<0.25 and not const0: out.append("sig"); off+=5
        else: break
    return out,off,nb
print(f"{'WIUID':13} {'current':22} {'inferred':22} lastfield-top")
print("-"*90)
res={}
for w in sorted(frames):
    rows=frames[w]
    if len(rows)<50 or w not in kinds_of: continue
    inf,off,nb=infer(rows,kinds_of[w])
    cur=["sw" if x=="switch" else "sig" for x in kinds_of[w]]
    res[w]=inf
    if cur!=inf:
        # show last inferred signal field's aspect spread
        li=len(inf)-1; lo=sum(2 if x=="sw" else 5 for x in inf[:li])
        top=""
        if inf and inf[-1]=="sig":
            vals=Counter(val(r,lo,5) for r in rows if len(r)>=lo+5)
            top=" ".join(f"{v}:{100*c//sum(vals.values())}%" for v,c in vals.most_common(4))
        print(f"{w:13} {' '.join(cur):22} {' '.join(inf):22} {top}")
