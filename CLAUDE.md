# iTergue

A terminal roguelike in Python. `uv run itergue` to play.

**Read these before doing anything.** They are the source of truth and this file
deliberately does not repeat them, because two descriptions of the same thing drift.

- `objectives.md` - the roadmap. What the game becomes, in order. Work comes from here.
- `.agents/skills/teach/MISSION.md` - why the project exists and what finishing means.
- `.agents/skills/teach/SKILL.md` - how work runs here. Read this before proposing
  anything: the loop is propose, plan, approve, branch, walk through, review.
- `.agents/skills/teach/NOTES.md` - who Vlad is, how he wants to be worked with, what is
  still open.

`.agents/` is gitignored, so nothing in the workspace is recoverable from git. Do not
delete files there.

## Gates

All five, under `uv run`, in the order CI runs them:

```
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run ty check src/
uv run pytest
uv build
```

Stdlib only. `dependencies = []` and it stays that way. `curses`, not Textual.
