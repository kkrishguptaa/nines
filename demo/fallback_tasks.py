"""Pre-seeded demo tasks with cheap executable checkers."""

from nines import Task

ADD = Task(
    prompt=(
        "Implement a Python function `add(a, b)` that returns the sum of two "
        "integers. Respond with ONLY the function source code."
    ),
    context="Property: add(a, b) == a + b for integers.",
)

# Checker artifact used when synthesis fails (--fallback path).
ADD_CHECKER = """
def check(output: str) -> bool:
    ns = {}
    try:
        exec(output, ns, ns)
    except Exception:
        return False
    fn = ns.get("add")
    if not callable(fn):
        return False
    try:
        return fn(2, 3) == 5 and fn(-1, 1) == 0 and fn(0, 0) == 0
    except Exception:
        return False
"""
