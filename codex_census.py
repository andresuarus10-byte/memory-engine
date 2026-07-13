#!/usr/bin/env python3
"""
codex_census.py — survey before ferry. STRICTLY READ-ONLY.
Walks the device, finds every JSON that smells like memories, classifies
and counts it, prints a manifest with anchors. Writes nothing, moves
nothing, imports nothing. The crown reviews, then we ferry.
"""
import hashlib, json, os

MAX_BYTES = 30 * 1024 * 1024   # skip anything larger

def _roots():
    here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    return [here, os.getcwd(), "/storage/emulated/0/Download",
            "/storage/emulated/0/Documents", "/storage/emulated/0",
            os.path.expanduser("~")]

def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

def classify(data):
    """Return (kind, record_count, date_range, sample) or None if not memory-like."""
    def daterange(stamps):
        stamps = sorted(s[:10] for s in stamps if isinstance(s, str) and len(s) >= 10)
        return f"{stamps[0]} .. {stamps[-1]}" if stamps else "?"

    if isinstance(data, dict) and isinstance(data.get("scrolls"), list):
        scrolls = data["scrolls"]
        stamps = [s.get("timestamp", "") for s in scrolls if isinstance(s, dict)]
        sample = ""
        for s in scrolls:
            ess = s.get("essence") if isinstance(s, dict) else None
            if ess:
                e0 = ess[0]
                sample = (e0 if isinstance(e0, str) else e0.get("text", ""))[:60]
                break
        return ("ENGINE-CODEX", len(scrolls), daterange(stamps), sample)

    if isinstance(data, list) and data and isinstance(data[0], dict) and "content" in data[0]:
        marker_keys = {"tags", "aliases", "status", "keywords", "project"}
        if marker_keys & set(data[0].keys()):
            stamps = [m.get("created_at", "") for m in data if isinstance(m, dict)]
            return ("SOPHON-STORE", len(data), daterange(stamps),
                    str(data[0].get("content", ""))[:60])

    # unknown but text-bearing json — worth a human glance
    prose_chars = 0
    def count_text(o, depth=0):
        nonlocal prose_chars
        if depth > 4 or prose_chars > 3000:
            return
        if isinstance(o, str):
            if len(o) >= 40 and " " in o:      # sentence-like, not tokens/paths
                prose_chars += len(o)
        elif isinstance(o, dict):
            for v in o.values():
                count_text(v, depth + 1)
        elif isinstance(o, list):
            for v in o[:50]:
                count_text(v, depth + 1)
    count_text(data)
    if prose_chars > 300:
        n = len(data) if isinstance(data, list) else len(data.keys()) if isinstance(data, dict) else 1
        return ("UNKNOWN-TEXTJSON", n, "?", "")
    return None

def main():
    print("=" * 60)
    print("  CODEX CENSUS — read-only survey of memory-like files")
    print("=" * 60)
    seen, findings, torn = set(), [], []
    for root in _roots():
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            if dirpath[len(root):].count(os.sep) >= 4:
                dirnames[:] = []
            dirnames[:] = [d for d in dirnames if d not in
                           ("node_modules", ".npm-global", ".cache", ".git",
                            "site-packages", "__pycache__", ".gradle")]
            for fn in filenames:
                low = fn.lower()
                if not (low.endswith(".json") or ".json.bak" in low or ".torn-" in low):
                    continue
                if low in ("package.json", "package-lock.json", "manifest.json",
                           "app.json", "composer.json") or "tsconfig" in low or ".schema" in low:
                    continue
                p = os.path.realpath(os.path.join(dirpath, fn))
                if p in seen:
                    continue
                seen.add(p)
                try:
                    size = os.path.getsize(p)
                    if size == 0:
                        torn.append((p, "empty"))
                        continue
                    if size > MAX_BYTES:
                        continue
                    data = json.load(open(p, encoding="utf-8"))
                except (ValueError, OSError):
                    torn.append((p, "unparseable"))
                    continue
                got = classify(data)
                if got:
                    findings.append((p, size) + got)

    findings.sort(key=lambda x: (x[2], -x[3]))
    total_records = 0
    for p, size, kind, n, dates, sample in findings:
        total_records += n
        print(f"\n[{kind}] {n} records  ({size:,} B)  {dates}")
        print(f"  {p}")
        print(f"  anchor16: {sha16(p)}" + (f"\n  sample: {sample}" if sample else ""))
    if torn:
        print(f"\n-- torn/empty json ({len(torn)}): --")
        for p, why in torn:
            print(f"  [{why}] {p}")
    print("\n" + "=" * 60)
    kinds = {}
    for f in findings:
        kinds[f[2]] = kinds.get(f[2], 0) + 1
    print(f"  files: {len(findings)} memory-like ({kinds}), {len(torn)} torn/empty")
    print(f"  candidate records across all files: {total_records}")
    print("  nothing was written, moved, or imported. survey only.")

if __name__ == "__main__":
    main()
