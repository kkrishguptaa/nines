import os

from nines.sandbox import _minimal_env, run_python


def test_minimal_env_strips_api_keys(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-other")
    monkeypatch.setenv("PATH", os.environ.get("PATH", "/usr/bin"))
    env = _minimal_env()
    assert "ANTHROPIC_API_KEY" not in env
    assert "OPENAI_API_KEY" not in env
    assert "PATH" in env


def test_run_python_child_cannot_see_api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-should-not-leak")
    code = (
        "import os\n"
        "def check(output: str) -> bool:\n"
        "    return 'ANTHROPIC_API_KEY' not in os.environ\n"
    )
    assert run_python(code, "check", ["x"]) is True
