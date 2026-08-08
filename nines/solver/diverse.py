from __future__ import annotations

MODELS = ("haiku", "sonnet", "opus")
EFFORTS = ("low", "medium", "high")
FRAMINGS = ("direct", "decompose", "checklist")


def diversity_configs(n: int) -> list[dict]:
    """Build ``n`` configs varying model tier, effort, and framing."""
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict] = []
    i = 0
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
        if i > max(n * 20, 50):
            break
    return unique[:n]
