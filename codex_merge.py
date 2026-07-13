#!/usr/bin/env python3
"""
codex_merge.py — the heirloom ferry.
Merges scrolls from an old engine-format codex into your canonical codex.
Keeps original timestamps, stamps provenance, skips duplicates by content.
Idempotent. Atomic save. The crown picks the source and the destination.
"""
import hashlib, json, os, shutil, sys
from datetime import datetime

CODEX_NAME = "my_codex.json"
ENGINE_NAME = "memory_engine_v3_3.py"
SOAK_TARGET = 66

def _roots():
    here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    return [here, os.getcwd(), "/storage/emulated/0/Download",
            "/storage/emulated/0/Documents", "/storage/emulated/0",
            os.path.expanduser("~")]

def find_all(name, exact=True):
    hits, seen = [], set()
    for root in _roots():
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            if dirpath[len(root):].count(os.sep) >= 4:
                dirnames[:] = []
            for fn in filenames:
                if (fn == name) if exact else (name in fn):
                    p = os.path.realpath(os.path.join(dirpath, fn))
                    if p not in seen:
                        seen.add(p); hits.append(p)
    return hits

def scroll_texts(scroll):
    out = []
    for e in scroll.get("essence", []):
        out.append(e if isinstance(e, str) else e.get("text", ""))
    return [t for t in out if t]

def content_key(texts):
    return hashlib.sha256("\n".join(t.strip() for t in texts).encode()).hexdigest()[:16]

def load_codex_state(path):
    try:
        state = json.load(open(path, encoding="utf-8"))
        if not isinstance(state, dict):
            return None
        return state if isinstance(state.get("scrolls"), list) else None
    except (ValueError, OSError):
        return None

def atomic_save(engine, codex_path):
    tmp = codex_path + ".tmp"
    engine.export_memory_state(tmp)
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    if os.path.exists(codex_path):
        try: shutil.copy2(codex_path, codex_path + ".bak")
        except OSError: pass
    os.replace(tmp, codex_path)

def choose(prompt, items, render):
    for i, it in enumerate(items, 1):
        print(f"    [{i}] {render(it)}")
    while True:
        pick = input(f"  {prompt} ").strip()
        if pick.isdigit() and 1 <= int(pick) <= len(items):
            return items[int(pick) - 1]

def main():
    engines = find_all(ENGINE_NAME)
    if not engines:
        print(f"Could not find {ENGINE_NAME} on this device."); sys.exit(1)
    sys.path.insert(0, os.path.dirname(engines[0]))
    from memory_engine_v3_3 import MemoryEngine

    # every engine-format codex on the device, big to small
    codexes = []
    for p in set(find_all(CODEX_NAME) + find_all(".json", exact=False)):
        if p.endswith(".tmp") or ".torn-" in p:
            continue
        state = load_codex_state(p)
        if state is not None:
            codexes.append((p, len(state["scrolls"])))
    codexes.sort(key=lambda x: -x[1])
    if len(codexes) < 2:
        print("Fewer than two engine-format codexes found — nothing to merge.")
        for p, n in codexes:
            print(f"  found: {n} scrolls  {p}")
        sys.exit(0)

    print("\n  Engine-format codexes on this device:")
    dest = choose("which is CANONICAL (merge INTO)?", codexes,
                  lambda c: f"{c[1]} scrolls  {c[0]}")
    sources = [c for c in codexes if c[0] != dest[0]]
    src = choose("which is the SOURCE (merge FROM)?", sources,
                 lambda c: f"{c[1]} scrolls  {c[0]}")

    eng = MemoryEngine()
    eng.load_memory_state(dest[0])
    existing = {content_key(scroll_texts(s)) for s in eng.scrolls}

    src_state = load_codex_state(src[0])
    added = skipped = 0
    for s in src_state["scrolls"]:
        texts = scroll_texts(s)
        if not texts:
            skipped += 1; continue
        key = content_key(texts)
        if key in existing:
            skipped += 1; continue
        ctx = dict(s.get("context", {}) or {})
        ctx.setdefault("theme", "heirloom")
        ctx["source"] = os.path.basename(src[0])
        ctx["ferry_id"] = key
        ts = s.get("timestamp") or datetime.now().isoformat()
        scroll = eng.compress_to_scroll(texts, ts, ctx)
        eng.update_codex(scroll)
        existing.add(key)
        added += 1

    atomic_save(eng, dest[0])
    h = hashlib.sha256(open(dest[0], "rb").read()).hexdigest()
    print("=" * 52)
    print("  CODEX MERGE — receipt")
    print("=" * 52)
    print(f"  from : {src[0]} ({src[1]} scrolls)")
    print(f"  into : {dest[0]}")
    print(f"  added {added}, skipped {skipped} (duplicates/empty)")
    print(f"  canonical now: {len(eng.scrolls)} scrolls — {len(eng.scrolls)}/{SOAK_TARGET} toward soak")
    print(f"  codex anchor: {h}")
    print("  original timestamps kept; provenance stamped; the source file untouched.")

if __name__ == "__main__":
    main()
