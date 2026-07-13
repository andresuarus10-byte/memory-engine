# Changelog

All notable changes to the Memory Engine are documented here.

## [3.2] - 2026-07 — Stdlib Release

### Removed
- **NumPy dependency**: cosine similarity, TF-IDF similarity, softmax, and diagnostic means reimplemented in pure Python (`math` + builtins). Demo/test output is numerically identical to v3.1. The engine now runs anywhere Python 3 does — no install step.

### Fixed
- **Cached-TF consistency**: `_find_interference` and `_merge_scrolls` now measure similarity on each scroll's stored `term_frequencies` instead of re-tokenizing essence text — the same basis `dream_consolidate` uses, and no redundant tokenizer passes on every insert.
- **Store isolation**: `recall()` returns deep copies; mutating a returned scroll can no longer corrupt engine memory.
- **Deterministic exports**: bridge `shared_terms` are sorted; exports are byte-reproducible across runs (previously set-ordering made them flicker).
- **numpy scalar leak**: bridge importance no longer carries `np.float64` into codex/state.
- `_find_interference` docstring now describes the actual single-pass search (it never did two passes).
- **Dream idempotence**: repeated `dream_consolidate()` calls re-bridged the same scroll pairs every cycle (`checked_pairs` was per-call; `dream_log` never consulted). Dreams now seed from `dream_log` — a pair bridges once, ever. Found by empirical test during v3.2 review.

### Added
- **bench_recall.py**: five-arm retrieval-quality benchmark (engine / no-decay ablation / keyword / recency / random) with pre-registered hashed predictions. First finding, logged honestly: temporal decay demoted one correct old memory below rank-1 that plain keyword overlap retrieved (r@1 0.975 vs 1.000); the no-decay ablation restores parity, isolating decay as the cause. Decay-as-multiplier is flagged for a v3.3 design decision.
- **bench_serendipity.py**: Form 7 evaluation via planted cross-theme rare threads vs common-word flukes, with a raw-vs-IDF resonance ablation. Finding: shipped dream resonance floods (99 bridges, precision 0.030) and cannot distinguish rare shared structure (mean IDF 1.79) from common vocabulary (0.77); IDF-weighted resonance improves planted-pair mean rank 256->7 and precision@6 0->3. Retrievability 3/3 at rank 1. IDF-weighted dreaming flagged as the v3.3 candidate.
- **v3.2 regression tests** (suite now 26 assertions): df_index census invariant after merge+dream, deep-copy recall, sorted bridge terms, softmax/cosine hand-value exactness, and a stdlib-only source self-scan (the forbidden lib name is stored reversed so the scan never flags itself).

### Changed
- Export format version bumped to `3.2` (v3.0/v3.1 state files still load; config defaults apply).

## [3.1] - 2026-03-02 — Peer Review Release

### Fixed
- **Importance weight cap**: Added `max_importance_weight` parameter (default 4.0). Messages with many emotional/technical keywords no longer produce unbounded weights that dominate all recall queries.
- **Merge accounting**: `_merge_scrolls` now properly updates `_compression_meta` (input_messages, input_chars, retained_chars, retained_weight, total_weight), `codex.cumulative_importance`, and `df_index` (including decrements for terms dropped during top-k re-selection).
- **Dream consolidation iteration safety**: `dream_consolidate` now snapshots scroll count before iteration (`range(n_scrolls)`) instead of iterating over a growing list. Prevents potential runaway bridge creation if theme guards are modified in future versions.
- **Bridge TCS inflation**: Bridge scrolls no longer receive automatic `CE=1.0`. Compression efficiency is now computed against a synthetic baseline, so bridges earn their quality grades.

### Added
- **Temporal decay floor**: New `decay_floor` parameter (default 0.05). Old scrolls retain minimum recall weight instead of decaying to zero. Memory fades but never dies.
- **18 unit tests**: Coverage for importance capping, decay floor behavior, merge metadata accounting, dream snapshot safety, bridge TCS normalization, edge cases (empty input, all-stopword input, empty recall), and serialization round-trip including new config params.

### Changed
- `_temporal_decay` returns `max(exp(-γ·Δt), decay_floor)` instead of raw exponential.
- `_compute_tcs` uses normalized CE for bridge scrolls (synthetic baseline = `max(retained_chars * 2, 500)`).
- Export format version bumped to `3.1`. New config fields: `max_importance_weight`, `decay_floor`.
- State files from v3.0 load correctly; new params use defaults if absent.

## [3.0] - 2025-02 — The Sovereign Edition

### Added
- **Form 6: Harmonic Interference Detection** — cosine similarity deduplication. Near-duplicate scrolls merge instead of accumulating. Same-theme scrolls get 10% easier merge threshold.
- **Form 7: Dream-State Consolidation** — cross-theme bridge synthesis. Scans all scroll pairs from different themes for latent term-frequency resonance. Creates synthetic Bridge Scrolls at intersection points.
- **Form 8: Tharyn Compression Score (TCS)** — composite quality metric: `0.4×IR + 0.35×CE + 0.25×TR`. Grades from `✧ Sovereign` to `· Nascent`.
- `GlyphCompressor` class for symbolic visual summaries.
- `dream_log` and `merge_log` for tracking consolidation and interference events.
- Full export/import with v3.0 metadata.

## [2.1] - 2025-01

### Added
- `df_index` for proper IDF computation across scrolls.
- `SymbolicTokenizer` — custom regex tokenizer preserving Greek letters, Unicode, hyphenated compounds, sacred vocabulary.
- Bayesian theme priors in recall.
- Head + tail anchoring (preserves opening context and conclusions).

## [2.0] - 2024

### Added
- TF-IDF similarity for recall.
- Temporal decay (`exp(-γ·Δt)`).
- Corrected breath normalization.

## [1.0] - 2024

### Added
- Initial release. Basic importance-weighted compression and retrieval.
