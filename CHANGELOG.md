# Changelog

All notable changes to the Memory Engine are documented here.

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
