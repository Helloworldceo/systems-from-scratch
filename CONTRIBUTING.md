# Contributing rules

These apply to every component, whether written by a person or an AI agent.

1. **One component per PR.** Take the first unticked item in `BACKLOG.md`.
2. **Folder:** `components/<snake_name>/` containing exactly
   - `<snake_name>.py`: the implementation
   - `test_<snake_name>.py`: pytest tests (import with `from <snake_name> import ...`)
   - `README.md`: same sections as the existing components (Problem, Design, complexity
     table, Trade-offs, Used in), with `**Category:** … · **Added:** YYYY-MM-DD`
3. **Python standard library only.** No new dependencies. Must work on Python 3.10+.
4. **Tests:** at least 5, covering normal use, edge cases and invalid input. Never call
   `time.sleep` or the network in tests: inject a fake clock or fake I/O instead.
5. **Clear code:** type hints, a module docstring, no dead code, roughly 80–300 lines.
6. **Bookkeeping in the same PR:** tick the item in `BACKLOG.md` and add a row to the
   Components table in `README.md`.
7. **PR title:** `feat(<snake_name>): add <Component name>`. CI must pass before merge.
8. Never commit secrets, tokens or personal data.
