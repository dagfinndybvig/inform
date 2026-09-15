# AGENTS.md — Inform 6 Tooling

This repo is an Inform 6 game project with headless testing tooling.
The README is the comprehensive reference; this file is the quick-rules
card an agent (or human) must follow in every session.

## Git workflow

- **Always start with `git pull --rebase origin main`.** The
  `compile-inform.yml` GitHub Actions workflow auto-commits the
  recompiled `.z5` to `main` on every source change, so the remote is
  almost always ahead of your local clone between sessions. Pull before
  starting work and again before pushing.
- **Never commit `.z5` files.** Only commit source (`.inf`) and doc
  changes. CI recompiles `adventure_lovecraft.z5` and commits it
  automatically. `test_lovecraft.z5` is gitignored — it must never be
  committed.
- **Push only source changes.** If `adventure_lovecraft.z5` shows up in
  `git status` as modified, do not stage it — CI will replace it.

## Checking CI status

- The `compile-inform.yml` and `pages` workflows run on every push to
  `main`. To check their status without authenticating `gh`, query the
  public GitHub API directly (this repo is public, so no token needed):

  ```bash
  curl -s "https://api.github.com/repos/dagfinndybvig/inform/actions/runs?per_page=5" \
    | python -c "import json,sys; [print(r['created_at'], r['name'], r['conclusion']) for r in json.load(sys.stdin)['workflow_runs']]"
  ```

  `gh` requires `GH_TOKEN` even for public repos, but the REST API is
  anonymous-readable for public repositories.

## Compiling

- Always pass a second argument to override the output filename:

  ```bash
  ./inform6_compiler/inform6.exe +inform6lib/inform6lib-master adventure_lovecraft.inf test_lovecraft.z5
  ```

- Without the second argument, the compiler writes to
  `adventure_lovecraft.z5` and overwrites the tracked canonical file.
- A clean compile prints only the version banner and exits 0. The one
  expected warning is "Defined constant IFID declared but not used" —
  this is harmless and expected.

## Testing

- **Use `ztest.py`, not Frotz.** Frotz is GUI-only and cannot be driven
  from a pipe. `ztest.py` is the headless Z-machine v5 interpreter for
  automated testing.
- Point `ztest.py` at `test_lovecraft.z5` (the local build), never at
  `adventure_lovecraft.z5` (the canonical CI build).
- **Regression-test after every source change.** Compile to
  `test_lovecraft.z5`, then run the full win path and verify the score
  is 90/90. A command sequence that achieves this:

  ```bash
  python ztest.py --mark --seed 1 --story test_lovecraft.z5 \
    "examine note" \
    "examine hearthstone" "take key" "take notebook" "take lantern" \
    "n" "e" "take twig" "w" "s" \
    "d" "switch on lantern" "examine crack" "pry coin with twig" "take coin" "u" \
    "n" "e" "n" "n" "e" "n" "n" \
    "unlock ornate box with rusty key" "open ornate box" "take flower" "eat flower" \
    "s" "e" "s" "s" "s" "w" "s" "d" \
    "enter clock" "give coin to goddess" "enter clock" "score"
  ```

  The final output must show "scored 90 out of a possible 90".

## Inform 6.44 compiler bug: comma-separated switch labels

The compiler generates incorrect dispatch code for comma-separated
action labels in `before`/`after`/`life` routines — only the first label
in the group reliably matches. **Always give each action its own label
and delegate to a shared helper routine:**

```inform
before [;
    Take: return HearthstoneReveal();
    Remove: return HearthstoneReveal();
    Push: return HearthstoneReveal();
    Pull: return HearthstoneReveal();
],
```

Never write `Take, Remove, Push, Pull:` — the latter three silently
fail and fall through to the library default.

## Scoring rules

- **Never `give X moved` for a `scored` object.** The library's
  `NoteObjectAcquisitions` awards `OBJECT_SCORE` only if the object
  does not yet have `moved`. If you set `moved` manually before the
  player takes the object, the score is silently skipped. Let the
  library set `moved` naturally on `take`. Use a separate flag (e.g.,
  `coin_pried`) to control `initial` description text instead.
- **Never append `[Your score has just gone up by N points.]` to
  response strings.** The library's `NotifyTheScore` (via
  `notify_mode = true`) prints this automatically for all score
  changes. Adding your own duplicates it. Just increment `score` and
  let the library announce it.
- `MAX_SCORE` is 90. The score breakdown: rooms (5 each x4 = 20),
  objects (4 each x5 = 20), milestones (10 + 10 + 20 + 10 = 50).
  Milestones: read note (10), eat flower (10), give coin to goddess (20),
  wake in Arkham (10).

## Grammar and library extensions

- `Extend 'verb'` must appear **after** `Include "Grammar"` — the
  library defines verbs inside `Grammar.h`, and `Extend` fails if the
  verb does not exist yet.
- Use `replace` when your new grammar line should override a matching
  library line (e.g., redirecting `smell <noun>` to a custom action).
  Without `replace`, the library's line wins and your redirect
  silently never fires.
- Use `first` when you want to intercept before the library grammar
  but keep the library lines as fallback (e.g., `Extend 'pry' first`).
- `get` is a separate verb from `take` in this library, not a synonym.
  If you extend one, you must extend the other separately.

## Library mechanics

- **Consult the library headers before implementing any mechanism.**
  The Inform 6 library is the source of truth. Grep the library headers
  (`linklpa.h`, `grammar.h`, `parser.h`, `verblib.h`) for the relevant
  property/routine and read the implementation before writing code.
  Guessing at semantics is how features silently fail.
- Use `PlayerTo(room, flag)` for all player movement, never raw
  `move player to room`. `PlayerTo` updates `location`/`real_location`,
  runs `MoveFloatingObjects`, and calls `AdjustLight`.
- Use flag 2 (`PlayerTo(room, 2)`) for teleports into a room with a
  `react_before` guardian — flag 0 generates a `Look` action that
  triggers `react_before` and can kill the player on arrival.
- `give X to Y` requires `Y` to have `has animate` (the `creature`
  grammar token). Add `has animate` to any NPC that must receive gifts.
- `->` nests under the last **top-level** object, not the last object
  of any depth. To nest an object inside a container that is itself a
  room child, make it top-level and `move` it in `Initialise`.
- `found_in` objects only appear if `MoveFloatingObjects` runs. Prefer
  `->` (static child) for objects that must always be in a room.

## Map generation

- `zmap.py` parses source and emits a Graphviz DOT map. Use it to
  verify room connections after adding or moving rooms.
- Dynamic connections (teleports, conditional exits) are not
  auto-detected — add them with `--edge`.

## Autoplay and world-gym (experimental)

- `autoplay/` contains an interactive headless player (`autoplay.py`)
  and a TCP gym server (`autoplay_server.py`) that serves any `.z5`
  file for agent-driven play. See `autoplay/AGENTS.md` for the
  operational guide.
- All autoplay tools subclass `ZMachine` from `ztest.py` — do not
  duplicate Z-machine logic in `autoplay/`. Fix opcode bugs in
  `ztest.py`.

## Further reading

This file is the quick-rules card. Read the full `README.md` for the
detailed reasoning, code examples, and library references behind every
rule listed here.
