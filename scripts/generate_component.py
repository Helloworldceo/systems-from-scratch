"""Build the next BACKLOG.md component with an LLM, test it, and record it.

Runs inside GitHub Actions. Needs a GEMINI_API_KEY (free tier) or
DEEPSEEK_API_KEY repo secret; optional LLM_MODEL overrides the model. Steps:
  1. Pick the first unticked backlog item without a "(skipped" note.
  2. Generate the implementation, the tests and the README (one call each).
  3. Run pytest; if it fails, send the error back for a fix (up to 2 times).
  4. On success tick the item and add a README row; otherwise mark it skipped.
Writes `message=<commit message>` to $GITHUB_OUTPUT.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
BACKLOG = ROOT / "BACKLOG.md"
README = ROOT / "README.md"
EXAMPLE = ROOT / "components" / "lru_cache"
MAX_FIXES = 2

ITEM_RE = re.compile(r"^- \[ \] (?P<title>.+?) — `(?P<name>[a-z0-9_]+)`\s*$")


def next_item() -> tuple[str, str, str, int] | None:
    category = ""
    for i, line in enumerate(BACKLOG.read_text().splitlines()):
        if line.startswith("## "):
            category = line[3:].strip()
        m = ITEM_RE.match(line)
        if m:
            return m["title"], m["name"], category, i
    return None


# OpenAI-compatible providers, used in this order when their key is set.
PROVIDERS = [
    ("GEMINI_API_KEY", "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
     ["gemini-2.5-flash", "gemini-flash-latest"]),
    ("DEEPSEEK_API_KEY", "https://api.deepseek.com/chat/completions", ["deepseek-chat"]),
]


def _targets() -> list[tuple[str, str, str]]:
    custom = os.environ.get("LLM_MODEL")
    out = []
    for env, url, models in PROVIDERS:
        key = os.environ.get(env)
        if key:
            out += [(url, key, m) for m in ([custom] if custom else []) + models]
    if not out:
        raise SystemExit("No API key: add a GEMINI_API_KEY or DEEPSEEK_API_KEY repo secret.")
    return out


def _call(url: str, key: str, model: str, system: str, user: str) -> str:
    body = json.dumps({
        "model": model,
        "temperature": 0.2,
        "stream": False,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=300) as r:
        raw = r.read().decode(errors="replace")
        status, ctype = r.status, r.headers.get("Content-Type")
    try:
        return json.loads(raw)["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise RuntimeError(f"unexpected response {status} {ctype}: {raw[:300]!r}")


def chat(system: str, user: str) -> str:
    import time
    errors = []
    for url, key, model in _targets():
        for _ in range(2):
            try:
                text = _call(url, key, model, system, user)
                print(f"[model ok: {model}]")
                return text
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")[:300]
                errors.append(f"{model}: HTTP {e.code} {detail}")
            except Exception as e:  # noqa: BLE001 - log and try the next option
                errors.append(f"{model}: {e}")
            print(errors[-1], file=sys.stderr)
            time.sleep(15)
    raise RuntimeError("all model calls failed:\n" + "\n".join(errors))


def strip_fences(text: str) -> str:
    m = re.search(r"```[a-zA-Z]*\n(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip() + "\n"


SYSTEM = (
    "You are a senior software engineer writing a teaching-quality component for the "
    "open-source repo 'systems-from-scratch'. Python 3.10+, standard library only, "
    "type hints, clear names, no dead code, no network, no sleeps. "
    "Reply with ONLY the requested file content inside one fenced code block."
)


def run_tests(folder: pathlib.Path) -> tuple[bool, str]:
    import shutil
    shutil.rmtree(folder / "__pycache__", ignore_errors=True)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                        str(folder)], capture_output=True, text=True, cwd=ROOT, env=env)
    return p.returncode == 0, (p.stdout + p.stderr)[-3500:]


def set_output(message: str) -> None:
    print(message)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"message={message}\n")


def main() -> None:
    _targets()  # fail fast if no API key is configured
    item = next_item()
    if item is None:
        set_output("")
        print("Backlog is empty.")
        return
    title, name, category, line_no = item
    today = dt.date.today().isoformat()
    folder = ROOT / "components" / name
    folder.mkdir(parents=True, exist_ok=True)
    impl_path, test_path, readme_path = (
        folder / f"{name}.py", folder / f"test_{name}.py", folder / "README.md")
    rules = (ROOT / "CONTRIBUTING.md").read_text()
    ex_impl = (EXAMPLE / "lru_cache.py").read_text()
    ex_test = (EXAMPLE / "test_lru_cache.py").read_text()
    ex_readme = (EXAMPLE / "README.md").read_text()

    impl = strip_fences(chat(SYSTEM, (
        f"Write `{name}.py` implementing: {title} (category: {category}).\n"
        "Aim for 80-300 lines with a module docstring explaining the idea. Validate "
        "inputs and raise ValueError on invalid arguments. If timing is involved, accept "
        "an injectable clock callable.\n\n"
        f"Repo rules:\n{rules}\n\nStyle example (lru_cache.py):\n```python\n{ex_impl}```")))
    impl_path.write_text(impl)

    tests = strip_fences(chat(SYSTEM, (
        f"Write `test_{name}.py`: 6-10 pytest tests for this module, imported with "
        f"`from {name} import ...`. Cover normal use, edge cases and invalid input. "
        "Deterministic only: no sleeps, no network, no randomness without a fixed seed.\n\n"
        f"Module `{name}.py`:\n```python\n{impl}```\n\n"
        f"Style example:\n```python\n{ex_test}```")))
    test_path.write_text(tests)

    ok, log = run_tests(folder)
    for attempt in range(MAX_FIXES):
        if ok:
            break
        print(f"tests failed, fix attempt {attempt + 1}\n{log}")
        fixed = chat(SYSTEM.replace("ONLY the requested file content inside one fenced "
                                    "code block", "the two files as instructed"), (
            "These tests fail. Fix the bug (in the implementation if the test is right, "
            "or in the test if its expectation is wrong). Return BOTH complete files, each "
            f"in its own fenced block, first `{name}.py` then `test_{name}.py`.\n\n"
            f"`{name}.py`:\n```python\n{impl_path.read_text()}```\n\n"
            f"`test_{name}.py`:\n```python\n{test_path.read_text()}```\n\n"
            f"pytest output:\n```\n{log}```"))
        blocks = re.findall(r"```[a-zA-Z]*\n(.*?)```", fixed, re.S)
        if len(blocks) >= 2:
            impl_path.write_text(blocks[0].strip() + "\n")
            test_path.write_text(blocks[1].strip() + "\n")
        ok, log = run_tests(folder)

    lines = BACKLOG.read_text().splitlines()
    if not ok:
        print(f"giving up on {name}\n{log}")
        import shutil
        shutil.rmtree(folder, ignore_errors=True)
        lines[line_no] += " (skipped: tests failed)"
        BACKLOG.write_text("\n".join(lines) + "\n")
        set_output(f"chore({name}): skip after failed generation")
        return

    readme = strip_fences(chat(SYSTEM, (
        f"Write the README.md for this component. Start with '# {title}' then the line "
        f"'**Category:** {category} · **Added:** {today}'. Then the sections Problem, Design "
        "(with a complexity table), Trade-offs and Used in, like the example. Be accurate "
        "about this exact implementation.\n\n"
        f"Implementation:\n```python\n{impl_path.read_text()}```\n\n"
        f"Example README:\n```markdown\n{ex_readme}```")))
    readme_path.write_text(readme)

    lines[line_no] = lines[line_no].replace("- [ ]", "- [x]", 1)
    BACKLOG.write_text("\n".join(lines) + "\n")

    rl = README.read_text().splitlines()
    last_row = max(i for i, l in enumerate(rl) if l.startswith("| ["))
    rl.insert(last_row + 1, f"| [{title}](components/{name}) | {category} | {today} |")
    README.write_text("\n".join(rl) + "\n")
    set_output(f"feat({name}): add {title}")


if __name__ == "__main__":
    main()
