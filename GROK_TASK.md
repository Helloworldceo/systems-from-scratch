You maintain the GitHub repo Helloworldceo/systems-from-scratch.

Every day:
1. Read BACKLOG.md and CONTRIBUTING.md on the main branch.
2. Take the FIRST unticked item in BACKLOG.md.
3. Create a branch named feat/<snake_name>.
4. Add components/<snake_name>/ with:
   - <snake_name>.py: implementation, Python standard library only, type hints, module docstring
   - test_<snake_name>.py: at least 5 pytest tests (normal use, edge cases, invalid input); no sleeps, no network; inject fake clocks or I/O
   - README.md: Problem, Design, complexity table, Trade-offs, Used in; header line "**Category:** <category> · **Added:** <today YYYY-MM-DD>"
   Follow the style of components/lru_cache and components/rate_limiter exactly.
5. In the same branch, tick the item in BACKLOG.md and add a row to the Components table in README.md.
6. Open a pull request to main titled "feat(<snake_name>): add <Component name>" with a 3–5 line summary.
7. Do NOT merge, do NOT push to main, do NOT touch other components, do NOT add dependencies or secrets.
If the backlog is empty, open an issue proposing 10 new items instead.
