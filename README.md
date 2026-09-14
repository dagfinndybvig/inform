<img width="1024" height="1024" alt="cover_text_adventure_v2" src="https://github.com/user-attachments/assets/948375f6-db28-4527-b27c-7769f81cc9b3" />

# Inform 6 Tooling

This repository is about **Inform 6 tooling** — the compiler, the standard
library, a Z-machine interpreter for manual play, `ztest.py` (a headless
Z-machine v5 interpreter for automated testing, validation, and debugging),
and `zmap.py` (a headless source parser that generates game-world maps for
visual verification of room layouts and connections), as well as a pipeline to compile and publish Inform files when sent to GitHub. The toolchain, testing
methodology, and library-mechanics documentation below apply to any Inform 6
game.

Respect all licences involved — the Inform 6 compiler, the standard library,
and Frotz each carry their own licence terms. See their respective directories
for details.

The original work in this repository — `ztest.py`, `zmap.py`, the "Goddess
in the Cellar" game source, the documentation, and the methodology notes — is
licensed under the MIT Licence. You are free to use, modify, and distribute
it.

The headless tooling is especilly aimed at agentic coding. To support that,
compilation is split into two paths:

- **Local testing** — compile to `test_lovecraft.z5` (gitignored) and drive it
  with `ztest.py` for automated regression tests. One throwaway file, never
  committed. See [Compile](#compile) and
  [Automated testing](#automated-testing-validation-and-debugging).
- **Publication** — the `compile-inform.yml` GitHub Actions workflow compiles
  `adventure_lovecraft.inf` to the canonical `adventure_lovecraft.z5` and
  commits it to `main`, where it is served via GitHub Pages. See
  [Compile](#compile).

The included game **"The Goddess in the Cellar"** is a small test project used
to exercise and validate the toolchain. It is a Lovecraftian text adventure: a
grandfather clock in a dark cellar teleports the player to an alien world, where
a flaming goddess demands a gold coin offering — any other action while in her
presence is punished by a lightning bolt.

Read this article on my motivation. The link between text adventures, ontology and agentic coding:<br>
https://www.linkedin.com/pulse/text-adventures-ontology-through-looking-glass-dagfinn-dybvig-eawie/

### Play in your browser

No install needed — play directly at **<https://dagfinndybvig.github.io/inform/>**.
The page loads a self-hosted copy of [Parchment](https://github.com/curiousdannii/parchment)
(a JavaScript Z-machine interpreter) which runs the compiled game in any modern
browser. Both the interpreter and the story file are served from the same GitHub
Pages domain, so there are no CORS or third-party caching issues. You type
commands like `look`, `examine hearthstone`, `go north`, `enter clock`,
`give coin to goddess`. Type `help` in the game for a list of standard commands.

## Toolchain

```
inform/
├── adventure_lovecraft.inf   # main source
├── adventure_lovecraft.z5     # compiled game (Z-machine v5, CI-produced, canonical)
├── test_lovecraft.z5          # local test build (gitignored, not committed)
├── adventure.inf / .z5        # original (non-Lovecraft) version
├── ztest.py                   # headless Z-machine v5 interpreter (testing)
├── zmap.py                    # source parser → Graphviz DOT map (debugging)
├── Z_TEST_TOOL.md             # ztest.py documentation
├── INFORM_MAP_TOOL.md         # zmap.py documentation
├── Z_SERVING_TOOL.md          # self-hosted Parchment serving documentation
├── parchment.html             # Parchment single-file build (browser play)
├── index.html                 # landing page, redirects to parchment.html
├── inform6_compiler/
│   └── inform6.exe            # Inform 6.44 compiler (Windows)
├── inform6lib/
│   └── inform6lib-master/     # Inform 6 library (parser.h, verblib.h, grammar.h, ...)
└── frotz/
    └── Frotz.exe              # Z-machine interpreter
```

### Compile

The repo keeps two distinct build outputs:

- **`adventure_lovecraft.z5`** — the canonical compiled game, tracked in git,
  served via GitHub Pages, and produced by the `compile-inform.yml` workflow.
  This is the only `.z5` file that should ever be committed.
- **`test_lovecraft.z5`** — a throwaway local build for testing before pushing.
  Gitignored. Produce it by passing a second argument to override the output
  filename:

```bash
./inform6_compiler/inform6.exe +inform6lib/inform6lib-master adventure_lovecraft.inf test_lovecraft.z5
```

The `+path` argument adds the library directory to the include search path so
`Include "Parser"`, `Include "VerbLib"`, and `Include "Grammar"` resolve. A
clean compile prints only the version banner and exits 0; any other output is
an error or warning.

`test_lovecraft.z5` is listed in `.gitignore` so it can never be committed by
accident. Always pass the second argument — without it, the compiler writes
to `adventure_lovecraft.z5` and overwrites the tracked canonical file.

> **Contributor workflow:** Always compile to `test_lovecraft.z5` locally.
> Commit the source change by itself; the `compile-inform.yml` GitHub Actions
> workflow recompiles `adventure_lovecraft.inf` and commits the updated
> `adventure_lovecraft.z5` to `main`.
>
> Because CI commits directly to `main`, the remote often moves ahead of your
> local clone between sessions. Run `git pull --rebase origin main` before
> starting work and again before pushing — otherwise your push will be
> rejected with "fetch first". `--rebase` keeps the history linear, preserving
> the alternating source-commit / auto-compile-commit pattern. Only rebase
> commits you have not pushed yet.

### Run

```bash
./frotz/Frotz.exe adventure_lovecraft.z5
```

To play a locally compiled test build instead, run `./frotz/Frotz.exe test_lovecraft.z5`.

For automated testing, pipe commands via stdin:

```bash
printf 'd\nenter clock\ngive coin to goddess\n' | ./frotz/Frotz.exe adventure_lovecraft.z5
```

### Automated testing, validation, and debugging

Frotz is GUI-only and cannot be driven from a pipe reliably. For automated
testing, validation, and debugging, use `ztest.py` — a headless Z-machine v5
interpreter that feeds scripted commands to the story file and prints all
output to stdout. Full documentation in [`Z_TEST_TOOL.md`](Z_TEST_TOOL.md).

Point ztest at your local `test_lovecraft.z5` build with `--story`, not the
canonical `adventure_lovecraft.z5`:

```bash
# regression-test a scoring path after a code change
python ztest.py --mark --seed 1 --story test_lovecraft.z5 "examine hearthstone" "take key" "n" "e" "n" "n" "e" "n" "n" "unlock ornate box with rusty key" "open ornate box" "take flower" "eat flower" "score"

# run a script of commands and diff against a baseline
python ztest.py --mark --seed 1 --story test_lovecraft.z5 --script tests/scoring.txt > tests/scoring.out
diff tests/scoring.out tests/scoring.baseline
```

Use it to validate that gameplay changes (verb routing, scoring, object
placement, room descriptions) produce the expected output, and to debug
issues by running targeted command sequences and inspecting the response
without launching the GUI.

#### Known gotcha: dropped objects may not appear in room listings

The bundled Inform 6 library (locally modified with the fix for L61122) only
prints the "You can also see X here." listing when at least one other object
in the room printed its `initial` or `describe` text during the same look.
If a room contains only moved (taken-and-dropped) objects, the listing is
silently omitted — the objects are still there and fully interactable
(`examine`, `take` work). This affects every object equally and is a
library-level behaviour, not a bug in the game source. When writing
regression tests, don't assert on the listing line for a room whose objects
have all been moved; assert on `examine`/`take` responses instead. Objects
with an `initial` property always show their initial text until first taken,
which is the reliable way to make an object visible on entry.

#### Known gotcha: comma-separated switch labels in before/life routines

The Inform 6.44 compiler has a bug where comma-separated action labels in a
`before` or `life` routine's switch only reliably match the first label in
the group. For example, `before [; Take, Remove, Push, Pull, LookUnder: ...];`
matches `Take` but silently fails to match `Push`, `Pull`, or `LookUnder` —
the action falls through to the library default, producing no custom output.
This also affects the library's own `LanguageLM` switch: `Pull,Push,Turn:`
(`english.h:1198`) only matches `Pull`, which is why `push <noun>` and
`turn <noun>` produce no output in the bundled game (confirmed against the
original canonical build). The workaround is to give each action its own
label and delegate to a shared helper routine:

```inform
before [;
    Take: return HearthstoneReveal();
    Remove: return HearthstoneReveal();
    Push: return HearthstoneReveal();
    Pull: return HearthstoneReveal();
],
```

This is a compiler bug, not a library bug — the labels are syntactically
valid Inform 6, but the compiler generates incorrect dispatch code for all
but the first label in a comma-separated group within `before`/`after`/`life`
routines. The library's `LanguageLM` switch in `english.h` uses the same
pattern and is affected the same way (which is why `push`/`turn` are broken
out of the box).

#### Known gotcha: give moved suppresses OBJECT_SCORE

`NoteObjectAcquisitions` (parser.h) awards `OBJECT_SCORE` (default 4) to each
`scored` object the first time it enters the player's possession, checking
`if (i hasnt moved)`. If `give coin moved` is called *before* the player takes
the object — e.g., in a `PrySub` routine that dislodges the coin — the
library sees `moved` already set and skips the award. The full win path then
scores 76/80 instead of 80/80. The fix: never `give X moved` manually for a
`scored` object; let the library set `moved` naturally on `take`. If the
`moved` flag was being used to suppress a stale `initial` description, replace
the string `initial` with a routine that checks the relevant flag (e.g.,
`coin_pried`) and returns the appropriate text.

### Map generation and visual debugging

For visual verification of room layouts and connections, use `zmap.py` — a
headless source parser that reads an `.inf` file and emits a Graphviz DOT map
of the game world. Full documentation in
[`INFORM_MAP_TOOL.md`](INFORM_MAP_TOOL.md).

```bash
# generate a DOT map from source (no compilation needed)
python zmap.py adventure_lovecraft.inf --edge "Cellar:Alien World:enter clock:dashed"

# write DOT to a file for rendering elsewhere
python zmap.py adventure_lovecraft.inf -o map.dot

# render to PNG if Graphviz is installed
python zmap.py adventure_lovecraft.inf --png map.png --edge "Cellar:Alien World:enter clock:dashed"
```

Use it to check that room connections are correct after adding or moving
rooms, to spot disconnected areas, and to visualize the world layout without
playing through. Dynamic connections (teleports, conditional exits set in
`before` routines) are not auto-detected — add them with `--edge`.

### Serving the game in a browser

The game is served via a self-hosted copy of Parchment on GitHub Pages.
The CI workflow (`.github/workflows/compile-inform.yml`) automatically
recompiles `adventure_lovecraft.inf` on every push to `main` and commits the
updated `.z5` back to the repo. GitHub Pages then serves both
`parchment.html` (the interpreter) and `adventure_lovecraft.z5` (the story
file) from the same domain, so the browser loads the game with no CORS
issues and no dependency on iplayif.com. Full documentation in
[`Z_SERVING_TOOL.md`](Z_SERVING_TOOL.md).

The CI workflow builds the Inform 6 compiler from source (matching the
bundled version) and uses the repo's bundled library, so the CI-compiled
binary is consistent with local compilation. It also creates case-sensitivity
symlinks for the library headers, which are lowercase on disk but referenced
with mixed case in the game source — a non-issue on Windows but a hard
failure on Linux.

## The game

### Map

```
Cottage --N--> Garden --E--> Forest --N--> Stone Circle --N--> Labyrinth South
  |D                                                              |
  v                                                          (ring of stones)
Cellar  ==[enter clock]==>  Alien World                    Altar Chamber
```

The Stone Circle is a clearing with a ring of standing stones. Going north
from the clearing funnels the player into a labyrinth of 5 rooms forming a
ring around the altar:

```
          Altar Chamber
              N|S
       Labyrinth North
      / E|        |W \
Labyrinth East    Labyrinth West
  |E
  v
Blind Alley
      \ S|        |E /
       Labyrinth South
           S|N
       Stone Circle
```

The player enters at Labyrinth South and must go east or west around the ring
to Labyrinth North, then north to the Altar Chamber where the altar and ornate
box are. A Blind Alley dead end branches east off Labyrinth East.

The Cellar is dark (no `light` attribute); the player must bring the brass
lantern (switchable, grants `light` when on) or fumble in darkness. Alien
World has `light`.

### Key objects

- **brass lantern** — `switchable`; its `after` routine gives/takes the `light`
  attribute on `SwitchOn`/`SwitchOff`.
- **loose hearthstone** — `static` object in the Cottage. The rusty key is
  hidden beneath it; `examine hearthstone` reveals the key (moves it to the
  Cottage). `take hearthstone`, `push hearthstone`, `pull hearthstone`, and
  `look under hearthstone` also work. The notebook's fourth passage hints that
  the key is hidden, but not where.
- **rusty key** — hidden under the hearthstone; unlocks the ornate box at the
  altar. Not visible or takeable until the hearthstone is examined.
- **grandfather clock** — `enterable container` in the Cellar. Entering it
  teleports the player (and the clock itself) between Cellar and Alien World.
- **twig** — in the Dark Forest. Needed to pry the gold coin from the Cellar
  crack; `pry coin with twig`, `take coin with twig`, and `put twig in crack`
  all route to the same `Pry` action.
- **gold coin** — hidden in a crack in the Cellar floor; the player must
  `examine crack` to discover it, then pry it loose with the twig before it
  can be taken (`take coin` fails with a hint until pried). The offering the
  goddess demands.
- **flaming goddess** — `animate` object in Alien World. Kills the player on
  any action except `give coin to goddess`; accepts the coin and becomes
  pacified (`goddess_appeased` flag), after which the player may leave.
- **indescribable horror** — a `found_in` floating object in Alien World.

### Scoring

The game has 80 points (`MAX_SCORE 80`), from three sources:

| Source | Items | Points |
|--------|-------|--------|
| Room exploration (`has scored`) | Garden, Forest, Cellar, Alien World | 5 each = 20 |
| Object acquisition (`has scored`) | notebook, rusty key, twig, flower, coin | 4 each = 20 |
| Milestone (manual `score +=`) | eat flower, give coin to goddess, return safely | 10 + 20 + 10 = 40 |
| **Total** | | **80** |

- Rooms with `has scored` award `ROOM_SCORE` (default 5) on first visit, via
  `ScoreArrival` (called by `LookSub`). The starting room (Cottage) is not
  scored.
- Objects with `has scored` award `OBJECT_SCORE` (default 4) when first taken,
  via `NoteObjectAcquisitions` (called every turn).
- The three narrative milestones award points manually with `score = score + N`
  and print `[Your score has just gone up by N points.]`.
- The Z-machine v5 status line shows the current score automatically; `score`
  prints it, and `fullscore` shows the places/things breakdown.

### Custom verbs

`inhale [noun]` — defined with `Verb 'inhale'` and an `InhaleSub` routine,
with special-case text for the flower and coin.

The library `smell`/`sniff` verb is extended to route `smell <noun>` to the
same `Inhale` action, so `smell flower`, `sniff flower`, and `inhale flower`
all produce the custom response. See "Extending a library verb" below.

`pry [noun] [with twig]` — the library already defines `pry`/`lever` (mapped
to Unlock), so the game extends it with `Extend 'pry' first` to intercept
`pry coin with twig` before the library grammar. A `PrySub` routine handles
the coin-in-crack puzzle: it requires the twig, sets the `coin_pried` flag,
and moves the coin to the Cellar. The coin's `initial` is a routine that
checks `coin_pried` to show the correct description after prying. Two gotchas:
the extension must come **after** `Include "Grammar"` (the library defines
`pry` inside `Grammar.h`), and `get` is a separate verb from `take` in this
library, so `Extend 'take' last` and `Extend 'get' last` both add
`* noun 'with' held -> Pry` to make `take coin with twig` and
`get coin with twig` parse.

## Methodology

**Consult the library first.** The Inform 6 library is the source of truth
for how every mechanism actually works. Before implementing or debugging any
behavior, grep the library headers for the relevant property/routine and read
the implementation. Guessing at semantics is how features silently fail to
integrate — the library often has non-obvious preconditions (attributes,
globals, scope) that a feature depends on.

**Standards must be constantly checked.** Inform 6 has precise, non-obvious requirements for object attributes and properties. Always verify against the library definitions (`linklpa.h` for attributes like `lockable`, `openable`, `container`; `grammar.h` for verb grammar). A single missing attribute (e.g., `openable` on a lockable container) can silently break a feature. **Always regression-test after changes** — even small edits can cascade and break unrelated functionality.

1. Goddess not appearing → read `MoveFloatingObjects` and `PlayerTo`.
2. Goddess not visible after teleport → read `LookSub` and the `thedark`
   handling in `LookSub`.
3. `give coin to goddess` rejected → read the `Give` grammar line and the
   `creature` token.

The library files worth knowing:

| File | Contains |
|------|----------|
| `linklpa.h` | property and attribute definitions (`found_in`, `react_before`, ...) |
| `grammar.h` | verb grammar lines and the `creature`/`noun`/`held` tokens |
| `parser.h` | the main loop, `BeforeRoutines`, `AfterRoutines`, `RunLife`, `deadflag` handling |
| `verblib.h` | action routines (`GiveSub`, `LookSub`), `MoveFloatingObjects`, `PlayerTo`, `AdjustLight` |

## Inform 6 library mechanics (with references)

### Object placement: `->` vs `found_in` vs top-level

- `Object -> foo` makes `foo` a child of the last **top-level** object
  declared before it — not the immediately preceding object of any depth.
  It is physically in that location from the start — no runtime movement
  needed. This is the simplest, most reliable way to place a static object
  in a room.
- `Object foo` (no arrow) is top-level (parentless). It must be moved somewhere
  with `move foo to <room>` (often in `Initialise`) or it floats.
- `found_in Room` marks a **floating object**. It is NOT placed automatically.
  The library's `MoveFloatingObjects` moves it into `location` when (and only
  when) `location` matches. See `verblib.h:1057` (`MoveFloatingObjects`).

**Pitfall:** `->` nests under the last top-level object, not the last object
of any nesting depth. If room R has a `->` child box, and box has a `->` child
flower, the flower becomes a sibling of box (both children of R), not a child
of box. There is no `-->` operator in Inform 6 for deeper nesting. To place an
object inside another object's child (e.g., an item inside a box inside a
room), make it top-level and `move` it into the container in `Initialise`:
`move flower to ornate_box;`. This is the same pattern used for the coin and
the grandfather clock.

**Pitfall:** `found_in` objects only appear if `MoveFloatingObjects` runs.
That routine is called from `PlayerTo` (`verblib.h:1094`) and from the normal
`Go` handler (`verblib.h:2107`). A custom teleport that uses raw
`move player to Room` bypasses both, so `found_in` objects never arrive. Use
`->` (static child) for objects that must always be in a room, or call
`PlayerTo` for the move.

### Moving the player: `PlayerTo` vs `move player`

Never use raw `move player to Room` for travel. It does not update the
`location` global, does not run `MoveFloatingObjects`, and does not adjust
light. `PlayerTo` (`verblib.h:1089`) does all of this:

```inform
[ PlayerTo newplace flag;
    NoteDeparture();
    move player to newplace;
    while (parent(newplace)) newplace = parent(newplace);
    location = real_location = newplace;
    MoveFloatingObjects(); AdjustLight(1);
    switch (flag) {
      0:    <Look>;
      1:    NoteArrival(); ScoreArrival();
      2:    LookSub(1);
    }
];
```

The `flag` argument controls the arrival behavior:

| flag | arrival |
|------|---------|
| 0 | generates a full `<Look>` action (runs `react_before`/`before`) |
| 1 | `NoteArrival` + `ScoreArrival` only (no look) |
| 2 | calls `LookSub(1)` directly (no action, no `react_before`) |

**Pitfall:** flag 0 generates a real `Look` action, which passes through
`BeforeRoutines` and thus `react_before` of every in-scope object. If an
in-scope object has a hostile `react_before` (e.g., the goddess), the player
is killed on arrival before they can type. Use flag 2 for teleports into a
room with a `react_before` guardian.

### Light and darkness

- A room with `has light` is self-lit. A room without it is dark unless a
  light-giving object (the player's lantern, with `has light` granted on
  switch-on) is present.
- When the player is in darkness, `location` is set to the special object
  `thedark` (not the real room). `real_location` still holds the real room.
- `LookSub` (`verblib.h:2271`) checks `if (location == thedark)` first and
  prints "Darkness" instead of the room description and its contents.
  This is why a raw `move player` from a dark room leaves the player in
  darkness even after arriving in a lit room: `location` was never updated
  off `thedark`. `PlayerTo` fixes this via `AdjustLight`.

### Action processing order

For each typed command, the library runs (`parser.h:5166`, `BeforeRoutines`
at `parser.h:5522`):

1. `GamePreRoutine`
2. `player.orders`
3. `react_before` of every object in scope (`parser.h:5527`)
4. `location.before`
5. the noun's `before`
6. the action routine (e.g., `GiveSub`)
7. `react_after`, `location.after`, noun's `after` (`AfterRoutines`, `parser.h:5536`)
8. end-of-turn sequence (daemons, each_turn, `AdjustLight`)

`react_before` returning true (`rtrue`) stops the action before it runs.
This is the mechanism the goddess uses to intercept every action.

### `life` and the `Give` action

- `GiveSub` (`verblib.h:1945`) validates the gift, then calls
  `RunLife(second, ##Give)` — i.e., the recipient's `life` routine.
- `life` is the standard way NPCs react to `Give`, `Show`, `Ask`, `Tell`,
  `Answer`, `Kiss`, `Attack`, etc.
- The `Give` verb grammar (`grammar.h:279-281`) uses the `creature` token,
  which **requires the recipient to have the `animate` attribute**. Without
  `animate`, the parser rejects `give X to Y` before `life` ever runs.

**Pitfall:** an NPC that must receive `give` must have `has animate`. A
statue/idol that is nonetheless a valid give-target needs `animate` even if
it is thematically inanimate.

### Death

- Set `deadflag = 1` to kill the player. The main loop (`parser.h:5166`)
  detects this, breaks the turn, and runs the death sequence
  (`parser.h:5323`): prints `*** You have died ***`, score, and the
  restart/restore/quit prompt.
- `deadflag = 2` is "win"; other values call `DeathMessage`.
- Setting `deadflag` from within `react_before` or `life` is safe — the
  loop checks it at turn end.

### Scoring

The library has a built-in scoring system with three layers. All three
are automatic once you set the right attributes/defaults — no manual code
needed for the first two.

**Room scoring** (`has scored` on rooms, `ROOM_SCORE` per room):

`ScoreArrival` (`verblib.h:2250`) is called from `LookSub` (line 2339) and
from `PlayerTo` with flag 1 (line 1097). It checks `if (location hasnt
visited)`, gives the `visited` attribute, and if the room has `scored`,
adds `ROOM_SCORE` (default 5) to `score` and `places_score`. The starting
room is scored too (the library calls `<Look>` after `Initialise`), so
omit `scored` from the start room if you don't want free points.

**Object scoring** (`has scored` on objects, `OBJECT_SCORE` per object):

`NoteObjectAcquisitions` (`parser.h:5475`) runs every turn. It loops over
objects in the player's inventory; any that haven't been `moved` get the
`moved` attribute, and if they have `scored`, `OBJECT_SCORE` (default 4)
is added to `score` and `things_score`. Points are awarded on first pickup,
not on subsequent turns.

**Task/milestone scoring** (manual `score += N`):

For one-time narrative milestones (eating the flower, giving the coin,
winning), award points manually with `score = score + N;` at the right
point in the code. Do **not** append a notification string — the library
prints its own automatically (see "Score notification" below).

```inform
Constant MAX_SCORE 80;

! In the flower's after routine:
Eat:
    flower_eaten = true;
    score = score + 10;
    "...description...";
```

### Score notification

The library has `notify_mode = true` by default (`parser.h:270`). At the
end of every turn, if `score` changed, `NotifyTheScore()` (`parser.h:5680`)
prints `[The score has just gone up by N points.]` automatically
(`english.h:1137`, `Miscellany` message 50). This covers **all** score
changes — room visits, object pickups, and manual `score +=`.

**Pitfall:** appending your own `[Your score has just gone up by N
points.]` to the response string duplicates the library notification.
The "sometimes" symptom: room/object scoring fires only the library
notification (correct), but manual milestones fire both your text and the
library's (duplicated). The fix is to never add notification text
yourself — just increment `score` and let the library announce it.
Players can toggle this with `notify on` / `notify off`.

`MAX_SCORE` sets the denominator for the score display. `ScoreSub`
(`verblib.h:1372`) prints `score out of MAX_SCORE`; `FullScoreSub`
(`verblib.h:1408`) adds a breakdown of `places_score` and `things_score`
subtotals. (The `task_scores`/`Achieved`/`PrintTaskName` system exists for
named task breakdowns in `fullscore`, but requires more setup and is
overkill for a small game — manual `score +=` is simpler.)

**Display:** In Z-machine v5, the status line shows score and turns
automatically (`DrawStatusLine`, `parser.h:6363`). `score` prints the
current score; `fullscore` prints the places/things breakdown.

### Extending a library verb

`Extend 'verb'` adds new grammar lines to an existing library verb; it must
appear **after** `Include "Grammar"` (which is where the library defines
the verb you are extending). Before that point the verb does not exist yet,
and `Extend` fails with "There is no previous grammar for the verb."

```inform
Include "Grammar";

Extend 'smell' replace
    * noun -> Inhale
    * -> Smell;
```

The `replace` keyword is essential here. Without it, `Extend` merely
**appends** new grammar lines after the library's existing ones. When two
lines both match the same input (e.g., the library's `* noun -> Smell` and
your `* noun -> Inhale`), the parser tries them in source order and the
library's line wins — so your redirect silently never fires. `replace`
discards the library's grammar for that verb and substitutes your lines
entirely, so your `* noun -> Inhale` takes priority. Include a fallback
`* -> Smell` (no noun) so bare `smell` still works via the library action.

**Pitfall:** `Extend 'smell' 'sniff'` is invalid syntax — `Extend` takes a
single verb name, not a list of synonyms. The library's `Verb 'smell' 'sniff'`
already groups `sniff` under `smell`, so extending `smell` automatically
covers `sniff`.

A third placement keyword is `first`: it puts your lines **before** the
library's, so yours are tried first without discarding the library grammar.
This is the right choice when the library already defines the verb with
different behavior you want to keep as a fallback:

```inform
Include "Grammar";

! The library defines pry/lever (mapped to Unlock); intercept first.
Extend 'pry' first
    * noun 'with' held -> Pry
    * noun -> Pry;
```

Note that `get` is a separate verb from `take` in this library (not a
synonym), so `take X with Y` and `get X with Y` each need their own
`Extend ... last * noun 'with' held -> Pry;` line to parse.

## Implementation details

### The clock teleport (`grandfather_clock.before`)

```inform
before [;
    Enter:
        if (parent(grandfather_clock) == Cellar) {
            move grandfather_clock to AlienWorld;
            print "...^";
            PlayerTo(AlienWorld, 2);
            rtrue;
        }
        else if (parent(grandfather_clock) == AlienWorld) {
            move grandfather_clock to Cellar;
            print "...^";
            PlayerTo(Cellar, 2);
            rtrue;
        }
        else "You step inside the clock, but nothing unusual happens.";
],
```

- The clock moves with the player (both sides work symmetrically) by
  checking `parent(grandfather_clock)` to decide direction.
- `PlayerTo(..., 2)` is essential: flag 2 calls `LookSub` directly without
  generating a `Look` action, so the goddess's `react_before` does not fire
  on arrival.
- `rtrue` from `before` stops the default `Enter` handling.

### The goddess (`react_before` + `life`)

```inform
react_before [;
    if (goddess_appeased) rfalse;                         # pacified: allow all
    if (action == ##Give && noun == coin && second == self) rfalse;  # let Give reach life
    deadflag = 1;                                         # everything else: death
    "...lightning bolt...";
],
life [;
    Give:
        if (noun == coin) {
            goddess_appeased = true;
            remove coin;
            "...accepted...";
        }
        deadflag = 1;                                     # wrong gift: death
        "...wrath...";
],
has animate;                                              # required for `give ... to goddess`
```

- `react_before` runs before every action while the goddess is in scope
  (i.e., while in Alien World). It allows only `give coin to goddess`
  through to `life`; all else is death.
- `life` handles the actual `Give`: the right coin pacifies her and is
  consumed (`remove coin`); a wrong gift is also death.
- `has animate` is mandatory so the `creature` token in the `Give` grammar
  accepts her as a recipient.
- After `goddess_appeased`, `react_before` returns false, so all actions
  (including `enter clock` to leave) are allowed.

### The coin

The coin is a top-level object (`Object coin`, no arrow). It does **not** start
in the Cellar — it starts nowhere. A `dark crack` object (a `->` child of the
Cellar, `has static`) has a `description` routine that, on first examination,
moves the coin to the Cellar:

```inform
Object -> crack "dark crack"
    with name 'crack' 'fissure' 'gap' 'crevice' 'floor',
    description [;
        if (parent(coin) == nothing) {
            move coin to Cellar;
            "A jagged fissure splits the flagstones ... a gold coin, wedged deep within the crack ...";
        }
        if (coin in Cellar)
            "... The gold coin glints within ...";
        "... Nothing remains within.";
    ],
    initial "A jagged crack splits the stone floor, its depths lost to shadow.",
    has static;
```

Before the crack is examined, the coin is nowhere (not in scope), so `take
coin` fails with "You can't see any such thing." After examining the crack,
the coin is moved to the Cellar, becomes visible, and can be taken normally.

The coin was kept as a top-level object (rather than a `->` child) because
inserting the goddess as a child of Alien World would otherwise have made the
coin (originally `Object -> coin` after the goddess) a child of the goddess.
Keeping it top-level and placing it explicitly (via the crack's `description`
routine) avoids the source-order parentage trap.

## Gotchas summary

- `found_in` objects need `MoveFloatingObjects` to run; raw `move player`
  does not trigger it. Prefer `->` for static room contents.
- `->` nests under the last top-level object, not the last object of any
  depth. A `->` child of a `->` child becomes a sibling, not a nested child.
  To nest an object inside a container that is itself a room child, make it
  top-level and `move` it into the container in `Initialise`.
- Raw `move player to Room` does not update `location`/`real_location` or
  adjust light. Use `PlayerTo`.
- `PlayerTo(..., 0)` generates a `Look` action that runs `react_before`;
  use flag 2 to skip it when arriving in a room with a `react_before`
  guardian.
- `give X to Y` requires `Y` to have `animate` (the `creature` grammar
  token). Add `has animate` to any NPC that must receive gifts.
- A room without `has light` is dark; in darkness `location == thedark`
  and the room's contents are not listed. `AdjustLight` (called by
  `PlayerTo`) restores the real `location` when light is available.
- Inserting a top-level object between a parent and its `->` children
  re-parents the children. Place static objects as direct `->` children of
  their room, or move them explicitly in `Initialise`.
- `Extend` must appear after `Include "Grammar"`, and needs `replace` when
  the new grammar line should override a matching library line (e.g.,
  redirecting `smell <noun>` to a custom action). Without `replace`, the
  library's line wins and the redirect silently never fires.
- `has scored` on a room awards `ROOM_SCORE` (5) on first visit, but only
  if the room is lit — `ScoreArrival` checks `location`, which is `thedark`
  in a dark room, so a dark room won't score until the player brings light.
  `has scored` on an object awards `OBJECT_SCORE` (4) on first pickup.
  Both are automatic; no manual code needed. Set `Constant MAX_SCORE N;`
  so the score display shows `N out of N`.
- For narrative milestones (not tied to rooms or pickup), use manual
  `score = score + N;` rather than the `task_scores`/`Achieved` system —
  simpler and sufficient for a small game.
- Do not append `[Your score has just gone up by N points.]` to response
  strings. The library's `NotifyTheScore` (`notify_mode = true` by default)
  prints this automatically at end of turn for all score changes. Adding
  your own duplicates it. Just increment `score` and let the library
  announce it.
- Descriptions should be logically consistent and non-redundant. A room's
  `description` and an object's `initial` both print on first view, so naming
  the same object in both produces a doubled description. Put the object's
  first appearance in exactly one place: either the room prose or the
  `initial` property, not both. When an object can appear in two rooms (e.g.,
  the clock, which moves between Cellar and AlienWorld), check which
  description fires where — `initial` only prints before the object has been
  moved/taken, so a moved object needs its presence described in the room
  prose of its new location.
- `RunRoutines` (`parser.h:5601`) transparently substitutes `real_location`
  for `thedark` when running `before`/`after`/`each_turn`/`react_before`/
  `react_after` etc. — every property except `initial`, `short_name`, and
  `description`. So a dark room's `before` and `each_turn` routines still fire
  even though `location == thedark`. `react_before` guardians are therefore
  active in a dark room, which matters if a custom teleport uses flag 0
  (generates a `Look` action) to arrive in a dark room guarded by one.
