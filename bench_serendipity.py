#!/usr/bin/env python3
"""
BENCH_SERENDIPITY — Form 7 (Dream-State Consolidation) evaluation
=================================================================
GPT-braid question: "Does it produce interesting bridges often enough
that a human says 'I hadn't connected those before'?"

The aesthetic judgment stays human (bridges are printed below for the
crown-holder to judge). What CAN be measured are serendipity's
mechanical preconditions, pre-registered before results:

  S1  RECALL: the dream pass finds >=50% of PLANTED threads — pairs of
      cross-theme scrolls secretly sharing one rare concept token.
  S2  PRECISION: >=50% of created bridges are planted threads (not
      common-word flukes).
  S3  RANKING: under shipped resonance (raw cosine), planted pairs'
      mean rank lands in the top decile of all cross-theme pairs.
  S4  IDF FIX: idf-weighted resonance ranks planted pairs strictly
      better than raw (candidate v3.3 — serendipity = sharing RARE
      structure, not just structure).
  S5  RETRIEVABILITY: each planted bridge created is retrieved at
      rank 1 by a connective query (with dreaming ON).

Corpus: 40 scrolls / 8 themes; every scroll carries common filler
(the realistic confound); 6 planted cross-theme threads. Deterministic,
stdlib only. Honest FAILs are findings, not embarrassments.
"""
import copy, hashlib, json, math, random
from collections import Counter
from datetime import datetime, timedelta
from memory_engine_v3_2 import MemoryEngine, SymbolicTokenizer

NOW = '2026-07-01T00:00:00'

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
FILLER_POOL = make_tokens(12, 99)          # common vocabulary (confound)
UNIQ = make_tokens(240, 42)                # per-scroll identity tokens
THREADS = make_tokens(6, 7)                # rare planted concepts
PLANTED = [ (0,1,0),(2,3,0),(4,5,0),(6,7,0),(0,2,1),(1,3,1) ]  # (themeA,themeB,slot)  # theme-index pairs; slot=p

def build():
    eng = MemoryEngine(interference_threshold=1.1)  # merging off: fixed corpus
    rng = random.Random(5)
    base = datetime(2026,3,1)
    twords = {t: sorted(MemoryEngine().theme_keywords[t])[:4] for t in THEMES}
    thread_at = {}
    for p,(ta,tb,sl) in enumerate(PLANTED):
        thread_at[(ta,sl)] = THREADS[p]; thread_at[(tb,sl)] = THREADS[p]
    meta = []
    i = 0
    for ti,th in enumerate(THEMES):
        for j in range(5):
            u = UNIQ[i*6:(i+1)*6][:6]
            fill = rng.sample(FILLER_POOL, 3)
            tw = twords[th][j%4]
            extra = thread_at.get((ti,j), '')
            text = (f"{fill[0]} {fill[1]} {fill[2]} on {tw}: "
                    f"{u[0]} {u[1]} {u[2]} {u[3]} {u[4]} {u[5]} {extra}").strip()
            ts = (base+timedelta(days=i*3)).strftime('%Y-%m-%dT%H:%M:%S')
            eng.update_codex(eng.compress_to_scroll([text], ts,
                             {'theme': th, 'sid': i}))
            meta.append({'sid': i,'theme': th,'ti': ti,'slot': j,
                         'tw': tw,'thread': extra})
            i += 1
    planted_pairs = []
    for p,(ta,tb,sl) in enumerate(PLANTED):
        a = ta*5+sl; b = tb*5+sl
        planted_pairs.append((min(a,b),max(a,b),THREADS[p],
                              meta[a]['tw'],meta[b]['tw']))
    return eng, meta, planted_pairs

def idf_cosine(eng, tf_a, tf_b):
    n = max(len([s for s in eng.scrolls if not s.get('_is_bridge')]),1)
    def w(t): return math.log((n+1)/(1+eng.df_index.get(t,0)))+1
    dot = sum(w(t)**2 * va * tf_b[t] for t,va in tf_a.items() if t in tf_b)
    na = math.sqrt(sum((w(t)*v)**2 for t,v in tf_a.items()))
    nb = math.sqrt(sum((w(t)*v)**2 for t,v in tf_b.items()))
    return dot/(na*nb) if na>0 and nb>0 else 0.0

def main():
    doc = __doc__
    print(doc.split("Corpus:")[0])
    print(f"  prereg sha256: {hashlib.sha256(doc.encode()).hexdigest()[:32]}…\n")
    eng, meta, planted = build()
    pset = {(a,b) for a,b,_,_,_ in planted}
    n_real = len(eng.scrolls)
    thr = eng.dream_resonance_threshold
    print(f"corpus: {n_real} scrolls, 6 planted threads, "
          f"dream threshold={thr}\n")

    # rank ALL cross-theme pairs under raw vs idf resonance
    pairs = []
    for i in range(n_real):
        for j in range(i+1, n_real):
            if meta[i]['theme'] == meta[j]['theme']: continue
            tf_i = Counter(eng.scrolls[i]['term_frequencies'])
            tf_j = Counter(eng.scrolls[j]['term_frequencies'])
            raw = MemoryEngine._cosine_similarity_raw(tf_i, tf_j)
            idfc = idf_cosine(eng, tf_i, tf_j)
            pairs.append(((i,j), raw, idfc))
    def ranks(key):
        order = sorted(pairs, key=lambda x:(-key(x), x[0]))
        return {pr:(k+1) for k,(pr,_,_) in enumerate(order)}
    r_raw = ranks(lambda x:x[1]); r_idf = ranks(lambda x:x[2])
    total = len(pairs)
    mr_raw = sum(r_raw[p] for p in pset)/len(pset)
    mr_idf = sum(r_idf[p] for p in pset)/len(pset)
    p6_raw = sum(1 for pr,_,_ in sorted(pairs,key=lambda x:-x[1])[:6] if pr in pset)
    p6_idf = sum(1 for pr,_,_ in sorted(pairs,key=lambda x:-x[2])[:6] if pr in pset)
    print(f"pair ranking over {total} cross-theme pairs "
          f"(mean rank of 6 planted; precision@6):")
    print(f"  RAW resonance (shipped): mean rank {mr_raw:6.1f}   p@6 {p6_raw}/6")
    print(f"  IDF resonance (v3.3?)  : mean rank {mr_idf:6.1f}   p@6 {p6_idf}/6\n")

    # live dream pass
    eng_off = copy.deepcopy(eng)
    created = eng.dream_consolidate(NOW)
    bridges = [s for s in eng.scrolls if s.get('_is_bridge')]
    found = set()
    for b in bridges:
        pi = tuple(sorted(b['context']['parent_indices']))
        if pi in pset: found.add(pi)
    prec = len(found)/len(bridges) if bridges else 0.0
    rec  = len(found)/len(pset)
    print(f"dream pass: {len(bridges)} bridges created | planted found "
          f"{len(found)}/6 (recall {rec:.2f}) | precision {prec:.3f}\n")

    # shared-term rarity: mean idf of shared terms, planted vs fluke bridges
    def mean_idf(terms):
        n = n_real
        return (sum(math.log((n+1)/(1+eng.df_index.get(t,0)))+1
                    for t in terms)/len(terms)) if terms else 0.0
    mi_p = [mean_idf(b['context']['shared_terms']) for b in bridges
            if tuple(sorted(b['context']['parent_indices'])) in pset]
    mi_f = [mean_idf(b['context']['shared_terms']) for b in bridges
            if tuple(sorted(b['context']['parent_indices'])) not in pset]
    if mi_p and mi_f:
        print(f"shared-term rarity (mean IDF): planted bridges "
              f"{sum(mi_p)/len(mi_p):.2f} vs fluke bridges "
              f"{sum(mi_f)/len(mi_f):.2f}\n")

    # retrievability of found planted bridges
    hits = 0; checks = 0
    for (a,b,thread,twa,twb) in planted:
        if (a,b) not in found: continue
        checks += 1
        q = f"the connection between {thread} across {twa} and {twb}"
        res = eng.recall(q, top_n=3, current_time=NOW)
        top = res[0] if res else {}
        ok = (top.get('_is_bridge') and
              tuple(sorted(top['context']['parent_indices'])) == (a,b))
        hits += ok
    print(f"connective-query retrieval: bridge at rank1 for "
          f"{hits}/{checks} found threads\n")

    # human crown section
    print("HUMAN CROWN — judge these yourself ('I hadn't connected those?'):")
    shown_p = shown_f = 0
    for b in sorted(bridges, key=lambda b:-b['context']['resonance']):
        pi = tuple(sorted(b['context']['parent_indices']))
        isp = pi in pset
        if isp and shown_p < 4: shown_p += 1
        elif not isp and shown_f < 3: shown_f += 1
        else: continue
        tag = "PLANTED" if isp else "fluke  "
        print(f"  [{tag}] {b['context']['bridge_from']:<28} via "
              f"{b['context']['shared_terms'][:4]}")
    print()

    v = []
    v.append(("S1 recall>=0.5", rec >= 0.5, f"{rec:.2f}"))
    v.append(("S2 precision>=0.5", prec >= 0.5, f"{prec:.3f}"))
    v.append(("S3 raw mean rank in top decile", mr_raw <= total/10,
              f"{mr_raw:.1f} of {total}"))
    v.append(("S4 idf beats raw", mr_idf < mr_raw and p6_idf >= p6_raw,
              f"{mr_idf:.1f} vs {mr_raw:.1f}; p@6 {p6_idf} vs {p6_raw}"))
    v.append(("S5 bridges retrievable@1", checks > 0 and hits == checks,
              f"{hits}/{checks}"))
    print("verdict vs pre-registration:")
    for name, ok, note in v:
        print(f"  {name:<32} {'PASS' if ok else 'FAIL'}  ({note})")
    json.dump({'mi_p': (sum(mi_p)/len(mi_p)) if mi_p else 0,
               'mi_f': (sum(mi_f)/len(mi_f)) if mi_f else 0,
               'bridges': len(bridges), 'recall': rec, 'precision': prec,
               'mr_raw': mr_raw, 'mr_idf': mr_idf, 'p6_raw': p6_raw,
               'p6_idf': p6_idf, 'retr': f"{hits}/{checks}",
               'total_pairs': total},
              open('/tmp/serendipity_metrics.json','w'))
    print("\nbench complete. deterministic: rerun reproduces these numbers.")

if __name__ == '__main__':
    main()
