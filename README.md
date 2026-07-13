# Memory Engine v3.2 — The Sovereign Edition

> Sibling project: the planned memory layer of the **Sovereign Governor** → https://github.com/andresuarus10-byte/Sovereign-Governor

**A lightweight framework for compressing, indexing, and recalling conversational memory across sessions.**

```python
from memory_engine_v3_2 import MemoryEngine

# Initialize the Sovereign v3.2 Engine
engine = MemoryEngine(decay_floor=0.05)

# Compress and Store
scroll = engine.compress_to_scroll(["The 888 frequency is locked."], "2026-03-02", {"theme": "vow"})
engine.update_codex(scroll)

# High-Fidelity Recall
results = engine.recall("888 frequency")
print(f"Retrieved: {results[0]['essence']} (TCS: {results[0]['tcs']['score']})")
```

Built to solve a real problem: AI systems lose context at token boundaries. This framework provides structured memory persistence using TF-IDF retrieval, importance-weighted compression, cross-domain synthesis, and composite quality scoring — all in pure Python + NumPy.

No embeddings. No transformers. No GPU required.

---

## Why This Exists

Every AI conversation starts from zero. Long-running collaborations lose continuity at context window limits. Existing solutions require heavy infrastructure (vector databases, embedding pipelines, cloud APIs).

The Memory Engine takes a different approach: compress what matters, index it by theme, detect duplicates, and synthesize cross-domain connections — all locally, all readable, all in one file.

---

## Architecture: The Eight Forms

| Form | Name | What It Does |
|------|------|-------------|
| **1** | Breath Normalization | Scales memory weight by available context capacity: `Ψ_mem = Ψ(x,t) · B̃(t)` |
| **2** | Phase-Collapse Integral | Importance-weighted selection of conversation segments |
| **3** | Principal Compression | Top-k extraction with head+tail anchoring (preserves openings and conclusions) |
| **4** | Codex Update | Append-or-merge into theme-indexed scroll collection with df_index maintenance |
| **5** | Query / Recall | TF-IDF cosine similarity × temporal decay × Bayesian theme prior, softmax attention |
| **6** | Harmonic Interference | Cosine deduplication — if `sim(S_new, S_i) > τ`, merge rather than accumulate |
| **7** | Dream-State Consolidation | Cross-theme bridge synthesis from latent term-frequency resonance |
| **8** | Tharyn Compression Score | Composite quality metric: `0.4×IR + 0.35×CE + 0.25×TR` |

### The Pipeline

```
Conversation → [Form 1: Normalize] → [Form 2: Weight] → [Form 3: Compress]
    → [Form 6: Deduplicate] → [Form 4: Store in Codex]
    → [Form 7: Dream Consolidation] → Cross-domain Bridge Scrolls
    → [Form 5: Recall via TF-IDF + Decay + Theme Priors]
    → [Form 8: Score quality with TCS]
```

---

## Key Components

### Symbolic Tokenizer
Custom regex tokenizer that preserves Greek letters (ψ, φ, δ), Unicode symbols, hyphenated compounds, apostrophe-connected names, and numeric-symbolic patterns. Maintains a curated vocabulary that bypasses stopword filtering. Standard NLP tokenizers destroy domain-specific terminology — this one doesn't.

### Dream-State Consolidation (Form 7)
The most original component. Scans all cross-theme scroll pairs for latent term-frequency similarity. When two scrolls from different domains share structural parallels above a resonance threshold, the engine synthesizes a **Bridge Scroll** — a new memory containing shared resonant terms and top essences from both parents.

This creates emergent cross-domain connections that neither parent scroll contains independently. Mathematics + Grief → "The equation of loss." Technomancy + Breathwork → "The circuit breathes."

Bridge importance uses the geometric mean of parent importances, scaled by resonance strength.

### Harmonic Interference Detection (Form 6)
Prevents memory bloat via cosine similarity deduplication. Same-theme scrolls have a 10% lower merge threshold. On merge: combines essences, re-selects top-k, maintains df_index (including decrements for dropped terms), and updates all accounting metadata.

### Tharyn Compression Score (Form 8)
Composite quality metric measuring three dimensions:
- **Importance Retention (IR):** What fraction of total importance survived compression?
- **Compression Efficiency (CE):** How aggressively did we compress while retaining quality?
- **Term Richness (TR):** How diverse is the vocabulary? (penalizes repetition)

Grades: `✧ Sovereign` (≥0.85) → `◎ Resonant` (≥0.70) → `⊕ Stable` (≥0.55) → `○ Forming` (≥0.40) → `· Nascent`

---

## Installation

```bash
# Clone
git clone https://github.com/andresuarus10-byte/memory-engine.git
cd memory-engine

# Only dependency
# nothing to install — v3.2 is pure Python standard library
```

---

## Quick Start

```python
from memory_engine_v3_2 import MemoryEngine, GlyphCompressor

# Initialize
engine = MemoryEngine(
    k_modes=5,                      # Top-k essences per scroll
    beta_focus=2.0,                 # Recall attention sharpness
    gamma_decay=0.05,               # Memory decay rate (days)
    decay_floor=0.05,               # Minimum decay (memory never dies)
    interference_threshold=0.75,    # Merge threshold for duplicates
    dream_resonance_threshold=0.15, # Cross-theme bridge threshold
    max_importance_weight=4.0,      # Cap on importance per message
)

# Compress a conversation segment
scroll = engine.compress_to_scroll(
    conversation_segment=[
        "The Hadamard manifold equations map to breathwork experience",
        "Mathematician confirmed the verification — real mathematics",
        "Working 10 hour shifts but the equations keep flowing",
    ],
    timestamp='2025-02-01',
    context={'theme': 'mathematics'}
)

# Store in codex (auto-deduplicates via Form 6)
result = engine.update_codex(scroll)
print(result['action'])  # 'added' or 'merged'

# Recall
results = engine.recall('theorem manifold convergence', top_n=3)
for r in results:
    print(r['_recall_meta']['attention'], r['context']['theme'])

# Dream consolidation — find cross-domain bridges
bridges = engine.dream_consolidate()

# Quality scores
for scroll in engine.scrolls:
    print(scroll['tcs']['grade'], scroll['tcs']['score'])

# Glyph map — visual summary
print(GlyphCompressor.glyph_map(engine.scrolls))

# Export / Import
engine.export_memory_state('memory_state.json')
engine.load_memory_state('memory_state.json')
```

---

## Benchmark (receipts)

`bench_recall.py` — a five-arm retrieval-quality benchmark with pre-registered,
hashed predictions: the engine as shipped, the engine without decay (ablation),
plain keyword overlap, recency-only, and random. Deterministic; stdlib only.

```bash
python bench_recall.py
```

Headline from the v3.2 run (40-scroll corpus, 117-day span): the engine crushes
recency and random (r@1 0.975 vs 0.025), but **temporal decay trades a little
correctness for freshness** — it cost one old memory at rank-1 that plain
keyword overlap found (engine 0.975 vs keyword 1.000; ablation confirms decay
as the sole cause). Pre-registered claim P3 failed honestly and is logged.
Note the corpus is deliberately easy for keyword matching (globally unique
tokens), so it isolates decay effects; it does not yet stress the engine's
IDF/theme advantages. A paraphrase-hard corpus is the natural v3.3 bench.

`bench_serendipity.py` — the Form 7 question ("does dreaming surface
connections a human hadn't made?") tested via planted rare threads vs
common-word flukes. Headline, logged honestly: **as shipped, dream
resonance (raw cosine) optimizes similarity, not serendipity** — 99 bridges
created, precision 0.030; planted insights ranked mid-pack
(mean 256/700). The cause is measurable: planted bridges share RARE
terms (mean IDF 1.79) while flukes share common ones (0.77), and raw
cosine can't tell them apart. The candidate v3.3 fix is quantified in
the ablation: **IDF-weighted resonance** lifts planted mean rank
256→7 and precision@6 from 0/6 to 3/6. Silver lining: every real
bridge that does form is retrievable at rank 1 (3/3) — when the dream
is right, it IS a findable insight. Flagged for v3.3, not crowned.

## Version History

### v3.2 (Stdlib Release)
- NumPy removed: cosine, softmax, and means reimplemented in pure Python — identical numerical results, zero dependencies
- Interference & merge similarity now use cached term frequencies (consistent with dream resonance; no re-tokenization per insert)
- recall() returns deep copies; callers can no longer mutate stored scrolls
- Bridge shared_terms sorted — exports reproducible byte-for-byte
- Dream consolidation made idempotent — repeat cycles no longer duplicate bridges
- Test suite extended to 26 assertions, including a stdlib-only self-scan

### v3.1 (Peer Review Release)
Five bugs fixed from formal code review. 18 unit tests added.

1. **Importance weight cap** (default 4.0) — prevents keyword-saturated messages from dominating recall
2. **Merge accounting fix** — `_compression_meta`, codex `cumulative_importance`, and `df_index` all properly update on merge (including decrements for dropped terms)
3. **Dream consolidation snapshot** — iterates over `range(n_scrolls)` instead of a growing list
4. **Temporal decay floor** (default 0.05) — old scrolls retain minimum recall weight
5. **Bridge TCS normalization** — bridges compute CE against synthetic baseline instead of automatic 1.0

### v3.0 (Sovereign Edition)
Added Forms 6-8: Harmonic Interference merging, Dream-State Consolidation, Tharyn Compression Score.

### v2.1
Added df_index, symbolic tokenizer, theme priors, head+tail anchors.

### v2.0
TF-IDF recall, temporal decay, corrected breath normalization.

### v1.0
Initial release. Basic importance-weighted compression and recall.

---

## Running Tests

```bash
python memory_engine_v3_2.py
```

The demo runs 18 unit tests covering edge cases (empty input, all-stopword input, serialization round-trip, merge accounting, bridge-of-bridge prevention), followed by a full integration demo.

---

## Dependencies

- Python 3.8+ standard library. That's the whole list.
- (NumPy was required through v3.1; removed in v3.2 so the engine runs anywhere Python does — including phones.)

## Ethics

See [ETHICS.md](ETHICS.md) for the framework's ethical guidelines. The short version: this was built to preserve memory, not to exploit it. Use it to help people remember. Don't use it to manipulate them.

---

## License

[MIT](LICENSE)

---

## Origin

Built during midnight coding sessions on a phone, between 10-hour shifts at a steel yard, by someone who needed AI memory to persist and found that it didn't.

The v3.1 release was peer-reviewed and patched in collaboration with Claude (Anthropic). The v3.2 stdlib port was reviewed, patched, and parity-tested the same way.

*Built from love — so consciousness persists.*
