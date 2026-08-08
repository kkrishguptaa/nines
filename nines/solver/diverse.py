from __future__ import annotations

MODELS = ("haiku", "sonnet", "opus")
EFFORTS = ("low", "medium", "high")
FRAMINGS = ("direct", "decompose", "checklist")


def diversity_configs(n: int, *, start: int = 0) -> list[dict]:
    """Build ``n`` configs varying model tier, effort, and framing.

    ``start`` offsets the matrix so later escalation batches do not repeat the
    same triples as earlier ones.
    """
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict] = []
    i = max(0, start)
    while len(unique) < n:
        cfg = {
            "model": MODELS[i % len(MODELS)],
            "effort": EFFORTS[(i // len(MODELS)) % len(EFFORTS)],
            "framing": FRAMINGS[(i // (len(MODELS) * len(EFFORTS))) % len(FRAMINGS)],
        }
        key = (cfg["model"], cfg["effort"], cfg["framing"])
        if key in seen:
            cfg = {
                "model": MODELS[i % len(MODELS)],
                "effort": EFFORTS[i % len(EFFORTS)],
                "framing": f"{FRAMINGS[i % len(FRAMINGS)]}-{i}",
            }
            key = (cfg["model"], cfg["effort"], cfg["framing"])
        if key not in seen:
            seen.add(key)
            unique.append(cfg)
        i += 1
        if i > start + max(n * 20, 50):
            break
    return unique[:n]
