#!/usr/bin/env python3
"""
BENCH_SERENDIPITY (v3.3-dream referee)
======================================
Same planted-thread corpus that convicted v3.2 (precision 0.030, planted
mean rank 217/700). Pre-registered bars for the tuned ear:

  D1  RECALL: all 6 planted threads bridged within 2 dream cycles.
  D2  PRECISION: >=0.5 of created bridges are planted (v3.2: 0.030).
  D3  BUDGET: no cycle creates more than dream_budget bridges.
  D4  RANKING: planted pairs' mean rank in top decile under the
      SHIPPED (IDF-weighted) resonance.
  D5  RETRIEVABILITY: every planted bridge retrieved at rank 1 by a
      connective query.

Deterministic; stdlib only. FAILs are findings.
"""
import copy, hashlib, json, math, random
from collections import Counter
from datetime import datetime, timedelta
from memory_engine_v3_3 import MemoryEngine, SymbolicTokenizer

NOW1, NOW2 = '2026-07-01T00:00:00', '2026-07-02T00:00:00'

def make_tokens(n, seed):
    cons, vow = "bdfgklmnprstvz", "aeiou"
    rng = random.Random(seed); out, seen = [], set()
    while len(out) < n:
        t = (rng.choice(cons)+rng.choice(vow)+rng.choice(cons)
             +rng.choice(vow)+rng.choice(cons))
        if t not in seen and t not in SymbolicTokenizer.STOPWORDS:
            seen.add(t); out.append(t)
    return out

THEMES = ['mathematics','emotional','breakthrough','connection',
          'technomancy','breathwork','memory','integration']
FILLER_POOL = make_tokens(12, 99)
UNIQ = make_tokens(240, 42)
THREADS = make_tokens(6, 7)
PLANTED = [ (0,1,0),(2,3,0),(4,5,0),(6,7,0),(0,2,1),(1,3,1) ]  # (themeA,themeB,slot)

def build():
    eng = MemoryEngine(interference_threshold=1.1)
    rng = random.Random(5)
    base = datetime(2026,3,1)
    twords = {t: sorted(MemoryEngine().theme_keywords[t])[:4] for t in THEMES}
    thread_at = {}
    for p,(ta,tb,sl) in enumerate(PLANTED):
        thread_at[(ta,sl)] = THREADS[p]; thread_at[(tb,sl)] = THREADS[p]
    meta = []; i = 0
    for ti,th in enumerate(THEMES):
        for j in range(5):
            u = UNIQ[i*6:(i+1)*6]
            fill = rng.sample(FILLER_POOL, 3)
            tw = twords[th][j%4]
            extra = thread_at.get((ti,j), '')
            text = (f"{fill[0]} {fill[1]} {fill[2]} on {tw}: "
                    f"{u[0]} {u[1]} {u[2]} {u[3]} {u[4]} {u[5]} {extra}").strip()
            ts = (base+timedelta(days=i*3)).strftime('%Y-%m-%dT%H:%M:%S')
            eng.update_codex(eng.compress_to_scroll([text], ts,
                             {'theme': th, 'sid': i}))
            meta.append({'sid': i,'theme': th,'tw': tw,'thread': extra})
            i += 1
    planted = []
    for p,(ta,tb,sl) in enumerate(PLANTED):
        a, b = ta*5+sl, tb*5+sl
        planted.append((min(a,b),max(a,b),THREADS[p],
                        meta[a]['tw'],meta[b]['tw']))
    return eng, meta, planted

def main():
    doc = __doc__
    print(doc)
    print(f"  prereg sha256: {hashlib.sha256(doc.encode()).hexdigest()[:32]}…\n")
    eng, meta, planted = build()
    pset = {(a,b) for a,b,_,_,_ in planted}
    n = len(eng.scrolls)
    print(f"corpus: {n} scrolls, 6 planted threads | floor="
          f"{eng.dream_resonance_threshold} budget={eng.dream_budget} "
          f"rare_anchor_df<={eng.dream_rare_anchor_df}\n")

    # pair ranking: v3.2 raw reference vs v3.3 shipped resonance (pre-dream)
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            if meta[i]['theme'] == meta[j]['theme']: continue
            tf_i = Counter(eng.scrolls[i]['term_frequencies'])
            tf_j = Counter(eng.scrolls[j]['term_frequencies'])
            raw = MemoryEngine._cosine_similarity_raw(tf_i, tf_j)
            shipped = eng._cross_resonance(eng.scrolls[i], eng.scrolls[j])
            pairs.append(((i,j), raw, shipped))
    total = len(pairs)
    def mean_rank(key):
        order = sorted(pairs, key=lambda x:(-key(x), x[0]))
        r = {pr:(k+1) for k,(pr,_,_) in enumerate(order)}
        return sum(r[p] for p in pset)/len(pset)
    mr_raw, mr_ship = mean_rank(lambda x:x[1]), mean_rank(lambda x:x[2])
    print(f"planted mean rank of {total} cross-theme pairs:")
    print(f"  v3.2 raw resonance (reference): {mr_raw:6.1f}")
    print(f"  v3.3 shipped (IDF-weighted)  : {mr_ship:6.1f}\n")

    # two dream cycles
    c1 = eng.dream_consolidate(NOW1)
    c2 = eng.dream_consolidate(NOW2)
    bridges = [s for s in eng.scrolls if s.get('_is_bridge')]
    found = {tuple(sorted(b['context']['parent_indices'])) for b in bridges} & pset
    prec = (len([b for b in bridges if tuple(sorted(
        b['context']['parent_indices'])) in pset]) / len(bridges)) if bridges else 0.0
    rec = len(found)/len(pset)
    print(f"dream cycle 1: {len(c1)} bridges | cycle 2: {len(c2)} | "
          f"total {len(bridges)}")
    print(f"planted found {len(found)}/6 (recall {rec:.2f}) | "
          f"precision {prec:.3f}\n")

    # retrievability
    hits = checks = 0
    for (a,b,thread,twa,twb) in planted:
        if (a,b) not in found: continue
        checks += 1
        q = f"the connection between {thread} across {twa} and {twb}"
        res = eng.recall(q, top_n=3, current_time=NOW2)
        top = res[0] if res else {}
        hits += bool(top.get('_is_bridge') and tuple(sorted(
            top['context']['parent_indices'])) == (a,b))
    print(f"connective-query retrieval: bridge at rank1 for {hits}/{checks}\n")

    print("HUMAN CROWN — the dreams this ear now has:")
    for b in sorted(bridges, key=lambda b:-b['context']['resonance']):
        pi = tuple(sorted(b['context']['parent_indices']))
        tag = "PLANTED" if pi in pset else "other  "
        print(f"  [{tag}] {b['context']['bridge_from']:<28} "
              f"rare_anchors={b['context'].get('rare_anchors')}")
    print()

    v = [("D1 recall==1.0 within 2 cycles", rec == 1.0, f"{rec:.2f}"),
         ("D2 precision>=0.5", prec >= 0.5, f"{prec:.3f} (v3.2 was 0.030)"),
         ("D3 per-cycle <= budget",
          len(c1) <= eng.dream_budget and len(c2) <= eng.dream_budget,
          f"{len(c1)},{len(c2)} <= {eng.dream_budget}"),
         ("D4 shipped mean rank top decile", mr_ship <= total/10,
          f"{mr_ship:.1f} of {total} (raw was {mr_raw:.1f})"),
         ("D5 bridges retrievable@1", checks > 0 and hits == checks,
          f"{hits}/{checks}")]
    print("verdict vs pre-registration:")
    allp = True
    for name, ok, note in v:
        allp &= ok
        print(f"  {name:<34} {'PASS' if ok else 'FAIL'}  ({note})")
    json.dump({'recall': rec,'precision': prec,'mr_ship': mr_ship,
               'mr_raw': mr_raw,'retr': f"{hits}/{checks}",'all': allp},
              open('/tmp/dream_metrics.json','w'))
    print("\nbench complete. deterministic: rerun reproduces these numbers.")

if __name__ == '__main__':
    main()
