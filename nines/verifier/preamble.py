"""Helpers injected into synthesized checkers (avoid embedding ``` literals)."""

# Built with chr() so this file and injected sources never contain fence runs.
FENCE = chr(96) * 3

CHECKER_PREAMBLE = f'''
def _nines_strip_fences(text: str) -> str:
    text = (text or "").strip()
    fence = "{FENCE}"
    if fence not in text:
        return text
    parts = text.split(fence)
    body = parts[1] if len(parts) > 1 else text
    lines = body.splitlines()
    if lines and lines[0].strip() and not lines[0].lstrip().startswith(
        ("def ", "class ", "import ", "from ", "@")
    ):
        lines = lines[1:]
    return chr(10).join(lines).strip() or text
'''


def wrap_checker_source(source: str) -> str:
    """Prefix checker source with fence-stripping helper."""
    src = source.strip()
    if "def _nines_strip_fences" in src:
        return src
    return CHECKER_PREAMBLE + "\n" + src
