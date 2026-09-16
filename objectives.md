# iTergue roadmap

What the game becomes. Agreed 2026-09-16. Why it matters is in
`.agents/skills/teach/MISSION.md`; this file is only the what and the order.

## The game

A terminal roguelike. **Three floors, about ten rooms each.**

One room fills the screen at a time, with doors leading out. There is no map and no
minimap: you remember the dungeon yourself. Each floor holds a **StoryKey**. On floors 1
and 2 it opens the door to the staircase down. On floor 3 it opens the treasure vault,
and reaching the treasure is the win. Enemies get harder by floor through new types, not
through bigger numbers on the same two.

Until step 2 below lands, a run can only end in death. That is the defect the whole
roadmap is arranged around.

## Where the game is today

One hand-authored 40x20 open room, `src/itergue/levels/level-1.json`. Two enemy types,
nine items, bump combat, an inventory with equipment slots, spells with targeting,
cooldowns, buffs and a time stop. 172 tests, four gates green. No stairs, no floors, no
rooms, no win.

---

## 1. Room model

Make rooms a thing the code knows about.

- Rooms become explicit rectangles on `Level`, carved into the same tile grid the game
  already uses. `Point`, `tile_at`, `walkable_neighbours` and the enemy BFS do not change.
- `render_level` clips to the current room's rectangle rather than to the screen. The
  camera is deleted.
- Doors become a tile type in `RoomObject`. Walking onto one puts you in the next room.
- Only the current room's enemies take turns. `end_turn` stops running a BFS for every
  enemy on the floor.
- Room dimensions are capped at a fixed maximum sized for an 80x24 terminal, **never
  computed from `curses.COLS`**. A room size that depends on the terminal means the same
  seed builds a different dungeon on a different screen, which would make step 3
  worthless.

## 2. Progression spine

Make a run finishable.

- Staircases, a locked door, the StoryKey, a floor counter on `Game`.
- Three floors, three keys. Floors 1 and 2: key opens the door to the stairs. Floor 3: key
  opens the treasure vault.
- Built on deliberately tiny placeholder floors, two or three rooms each, thrown away in
  step 3. Enough to prove a key opens a door and a staircase changes floors, and no more.

## 3. Generation

Replace the placeholder floors.

- Hybrid: the layout is generated, a few marked rooms are filled from an authored pool so
  the key room and the vault are designed rather than stumbled into.
- Seeded and reproducible. The same seed builds the same dungeon.
- Floors grow to about ten rooms here.
- `Level.__init__` splits into a `from_json` classmethod at this point, not before, once
  the generator's real requirements are visible.
- The Python: randomness, seeding, and testing code whose output changes every run. None
  of it touched so far.

## 4. Content

Make floors 2 and 3 feel different from floor 1.

- New enemy types per floor in `ENEMY_TYPES`, each with its own stats and glyph. The
  generator places them by floor.
- Area damage, moved here from the consumable-effects roadmap. One pass over
  `ITEM_TYPES` and `ENEMY_TYPES` instead of two.
- Poison via `strike` is the obvious companion, and it is the first thing that would ever
  write `Enemy.effects`, which Lesson 23 left deliberately unused.

## 5. Endings

- Main menu, death screen and win screen, built as one pass. All three are the same state
  machine around `start()`: new game, resume, play again, quit.
- The menu has been parked in the notes since Lesson 21 for exactly this reason. A menu
  written before the win screen exists gets rewritten when the win screen arrives.

## 6. Presentation

- Layout, panels and colour, inside `curses`. The HUD currently shows no active effect, no
  cooldown and no turn counter.
- Not Textual. It would obsolete `render.py`, `show_screen`, `init_colors`, the
  `ScreenDrawer` type and most of `test_layering.py`, and leave the game no more finished.
  If it ever happens it is the last feature, not the next one.

---

## On the list, not committed

- **`README.md`**, written once the game is finished. Player-facing first: what iTergue is,
  how to install and run it, the controls, the goal of a run. Contributor notes after.
  It is currently zero bytes and `pyproject.toml` ships it in the wheel.
- **Save and load.** Deferred until the game is playable and winnable. A three-floor run
  fits in one sitting, so permadeath and restart is the genre-correct answer for now. If
  runs get longer, save-and-quit (not save-anywhere, which would undo the difficulty
  curve) becomes worth doing, and the serialization work comes with it.
- **Riddles.** A riddle is another way to open a door, so the StoryKey mechanic is already
  the hook. Its own discussion.

## Removed, not deferred

- **Field of view.** One room per screen already does the job FOV was for. A fully drawn
  floor behind a scrolling camera was the problem; there is no such floor any more.
