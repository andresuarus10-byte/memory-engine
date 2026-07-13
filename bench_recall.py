#!/usr/bin/env python3
"""
BENCH_RECALL — retrieval-quality benchmark for Memory Engine v3.2
=================================================================
Question: does the engine's recall math (TF-IDF x temporal decay x
theme prior) actually find the right memory better than dumb baselines?

Receipts before crowns: predictions are pre-registered (and hashed)
BEFORE results are computed. Fully deterministic; stdlib only.

Arms:
  ENGINE      recall() as shipped (tfidf x decay x prior)
  ENGINE-DEC  same relevance without the decay factor (isolates decay)
  KEYWORD     plain TF cosine overlap (no idf, no decay, no prior)
  RECENCY     newest-first, ignores the query
  RANDOM      seeded shuffles, averaged over 200 reps

Corpus: 40 synthetic scrolls (5 per theme x 8 themes), each carrying
6 globally-unique tokens + 2 real theme words + shared filler, spread
over ~117 days. Queries: 3 of the 6 unique tokens + 1 theme word.
Synthetic-by-design: isolates the ranking math from content luck.
Interference merging disabled (threshold>1) so the corpus stays fixed:
each scroll IS a distinct memory by construction.
"""
import copy, hashlib, math, random
from collections import Counter
from datetime import datetime, timedelta
from memory_engine_v3_3 import MemoryEngine, SymbolicTokenizer

NOW = '2026-07-01T00:00:00'
K_LIST = (1, 3, 5)
RAND_REPS = 200

# ---------- deterministic corpus ----------
def make_tokens(n):
    cons, vow = "bdfgklmnprstvz", "aeiou"
    toks, seen = [], set()
    rng = random.Random(42)
    while len(toks) < n:
        t = (rng.choice(cons) + rng.choice(vow) + rng.choice(cons)
             + rng.choice(vow) + rng.choice(cons))
        if t not in seen and t not in SymbolicTokenizer.STOPWORDS:
            seen.add(t); toks.append(t)
    return toks

THEMES = ['mathematics', 'emotional', 'breakthrough', 'connection',
          'technomancy', 'breathwork', 'memory', 'integration']

def build():
    eng = MemoryEngine(interference_threshold=1.1)  # merging off: fixed corpus
    uniq = make_tokens(240)
    theme_words = {t: sorted(MemoryEngine().theme_keywords[t])[:4] for t in THEMES}
    scrolls, queries = [], []
    base = datetime(2026, 3, 1)
    i = 0
    for th in THEMES:
        for j in range(5):
            u = uniq[i*6:(i+1)*6]
            tw = theme_words[th][j % 4], theme_words[th][(j+1) % 4]
            text = (f"field notes regarding {tw[0]} and {tw[1]} today: "
                    f"{u[0]} {u[1]} {u[2]} {u[3]} {u[4]} {u[5]} observed clearly")
            ts = (base + timedelta(days=i*3)).strftime('%Y-%m-%dT%H:%M:%S')
            eng.update_codex(eng.compress_to_scroll(
                [text], ts, {'theme': th, 'sid': i}))
            queries.append({'sid': i, 'ts': ts,
                            'q': f"remind me about {u[0]} {u[1]} {u[2]} and {tw[0]}"})
            i += 1
    return eng, queries

# ---------- rankings per arm (list of sids, best first) ----------
def sid_of(s): return s['context']['sid']

def rank_engine(eng, q):
    snap_la = [s['last_accessed'] for s in eng.scrolls]
    snap_al = dict(eng.access_log)
    res = eng.recall(q, top_n=len(eng.scrolls), current_time=NOW)
    for s, la in zip(eng.scrolls, snap_la): s['last_accessed'] = la
    eng.access_log = snap_al
    return [sid_of(s) for s in res]

def rank_engine_nodecay(eng, q):
    qtf = Counter(SymbolicTokenizer.tokenize(q))
    qth = eng._detect_themes(set(qtf))
    scored = [(sid_of(s),
               eng._tfidf_similarity(qtf, s) * eng._theme_prior(s, qth))
              for s in eng.scrolls]
    scored.sort(key=lambda x: (-x[1], x[0]))
    return [sid for sid, _ in scored]

def rank_keyword(eng, q):
    qtf = Counter(SymbolicTokenizer.tokenize(q))
    scored = [(sid_of(s), MemoryEngine._cosine_similarity_raw(
        qtf, Counter(s['term_frequencies']))) for s in eng.scrolls]
    scored.sort(key=lambda x: (-x[1], x[0]))
    return [sid for sid, _ in scored]

def rank_recency(eng, q):
    scored = sorted(eng.scrolls, key=lambda s: s['timestamp'], reverse=True)
    return [sid_of(s) for s in scored]

# ---------- metrics ----------
def score(rankings, queries):
    hits = {k: 0 for k in K_LIST}; mrr = 0.0
    per_q_rank = []
    for r, qq in zip(rankings, queries):
        pos = r.index(qq['sid']) + 1
        per_q_rank.append(pos)
        mrr += 1.0 / pos
        for k in K_LIST:
            if pos <= k: hits[k] += 1
    n = len(queries)
    return ({k: hits[k]/n for k in K_LIST}, mrr/n, per_q_rank)

def main():
    prereg = (
        "PRE-REGISTERED (before results):\n"
        "  P1: ENGINE recall@1 beats RANDOM by >3x\n"
        "  P2: ENGINE recall@1 >= RECENCY recall@1\n"
        "  P3: ENGINE recall@1 >= KEYWORD recall@1  (the engine's implicit claim)\n"
        "  P4: if P3 fails, the gap concentrates in OLD-half targets (decay cost),\n"
        "      and ENGINE-DEC ~= KEYWORD (decay identified as the cause)\n")
    print(prereg)
    print(f"  prereg sha256: {hashlib.sha256(prereg.encode()).hexdigest()[:32]}…\n")

    eng, queries = build()
    n = len(eng.scrolls)
    print(f"corpus: {n} scrolls / 8 themes / span {queries[0]['ts'][:10]} -> "
          f"{queries[-1]['ts'][:10]} / now={NOW[:10]} / merging disabled\n")

    arms = {}
    arms['ENGINE'] = [rank_engine(eng, q['q']) for q in queries]
    arms['ENGINE-DEC'] = [rank_engine_nodecay(eng, q['q']) for q in queries]
    arms['KEYWORD'] = [rank_keyword(eng, q['q']) for q in queries]
    arms['RECENCY'] = [rank_recency(eng, q['q']) for q in queries]
    rng = random.Random(7)
    rr = {k: 0.0 for k in K_LIST}; rmrr = 0.0
    for _ in range(RAND_REPS):
        ranks = []
        for q in queries:
            order = list(range(n)); rng.shuffle(order); ranks.append(order)
        h, m, _ = score(ranks, queries)
        for k in K_LIST: rr[k] += h[k]
        rmrr += m
    results = {}
    for name, ranks in arms.items():
        results[name] = score(ranks, queries)
    results['RANDOM'] = ({k: rr[k]/RAND_REPS for k in K_LIST}, rmrr/RAND_REPS, None)

    print(f"{'arm':<11} {'r@1':>6} {'r@3':>6} {'r@5':>6} {'MRR':>7}")
    for name in ['ENGINE', 'ENGINE-DEC', 'KEYWORD', 'RECENCY', 'RANDOM']:
        h, m, _ = results[name]
        print(f"{name:<11} {h[1]:>6.3f} {h[3]:>6.3f} {h[5]:>6.3f} {m:>7.3f}")

    # old/new breakdown on recall@1 for the query's target age
    median = sorted(q['ts'] for q in queries)[n//2]
    def split_r1(per_q):
        old = [1 for r, q in zip(per_q, queries) if q['ts'] < median and r == 1]
        new = [1 for r, q in zip(per_q, queries) if q['ts'] >= median and r == 1]
        n_old = sum(1 for q in queries if q['ts'] < median)
        return len(old)/n_old, len(new)/(n - n_old)
    print("\nrecall@1 by target age (old half vs new half):")
    for name in ['ENGINE', 'ENGINE-DEC', 'KEYWORD']:
        o, w = split_r1(results[name][2])
        print(f"  {name:<11} old {o:.3f} | new {w:.3f}")

    e1 = results['ENGINE'][0][1]; k1 = results['KEYWORD'][0][1]
    r1 = results['RECENCY'][0][1]; z1 = results['RANDOM'][0][1]
    d1 = results['ENGINE-DEC'][0][1]
    print("\nverdict vs pre-registration:")
    print(f"  P1 {'PASS' if e1 > 3*z1 else 'FAIL'}  (engine {e1:.3f} vs 3x random {3*z1:.3f})")
    print(f"  P2 {'PASS' if e1 >= r1 else 'FAIL'}  (engine {e1:.3f} vs recency {r1:.3f})")
    print(f"  P3 {'PASS' if e1 >= k1 else 'FAIL'}  (engine {e1:.3f} vs keyword {k1:.3f})")
    if e1 < k1:
        eo, en_ = split_r1(results['ENGINE'][2])
        print(f"  P4 gap check: engine old-half r@1 {eo:.3f} vs new-half {en_:.3f}; "
              f"ENGINE-DEC r@1 {d1:.3f} vs KEYWORD {k1:.3f}")
    print("\nbench complete. deterministic: rerun reproduces these numbers.")

if __name__ == '__main__':
    main()
