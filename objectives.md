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

One hand-authored floor, `src/itergue/levels/level-1.json`, four rooms joined by three
doors, one room on screen at a time. Two enemy types, nine items, bump combat, an
inventory with equipment slots, spells with targeting, cooldowns, buffs and a time stop.
190 tests, five gates green. No stairs, no floors, no key, no win.

---

## 1. Room model (done 2026-09-19)

What shipped, which is not quite what this step described. Full account in
`.agents/skills/teach/plans/0001-the-room-model.md`.

- Rooms are **discovered**, not declared: `Level` flood fills the floor at load, bounded
  by walls and doors, so a room takes any shape and a generator only has to carve.
  `Point`, `tile_at`, `walkable_neighbours` and the enemy BFS were not touched.
- `RoomObject.DOOR`. Walking onto a door puts you in the next room; a doorway keeps
  showing the room you are leaving, since a door belongs to neither.
- `render_level` draws one room and its walls. The camera was **not** deleted: it is
  derived from the room instead of the player, and falls back to following the player on
  any axis where the room does not fit the terminal.
- `Game.current_room`. Only that room's enemies take turns.
- `MAX_ROOM = Point(80, 17)`, a fixed constant and never the live terminal size, so one
  seed builds one dungeon everywhere. A room over it is a `LevelError`, as is a
  `player_start` off the floor.

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
- **The generator must not strand anything.** A floor region nothing connects to is
  discovered as a room like any other, harmless today because the player can never be in
  it, and fatal here: a StoryKey placed in one makes the floor unwinnable.

## 4. Content

Make floors 2 and 3 feel different from floor 1.

- New enemy types per floor in `ENEMY_TYPES`, each with its own stats and glyph. The
  generator places them by floor.
- Area damage, moved here from the consumable-effects roadmap. One pass over
  `ITEM_TYPES` and `ENEMY_TYPES` instead of two.
- Poison via `strike` is the obvious companion, and it is the first thing that would ever
  write `Enemy.effects`, which Lesson 23 left deliberately unused.
- Enemies that follow the player through a door. Today they stay in their room. The
  version worth building is an enemy that saw you leave, not the whole floor walking.

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
