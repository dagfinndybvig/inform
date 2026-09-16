# Progress Report: Playing Curses

This report summarises the progress of an AI agent playing Graham
Nelson's *Curses* (1993) using the Z-machine gym server in this
repo's `autoplay/` folder. The game is played one command at a time
over TCP. At first there was no save/restore and each session
replayed from the opening; mid-campaign a full snapshot system
(`__save`/`__load`) was introduced (see the final update below),
which changed the way the whole game was played.

## Sessions and score

Across multiple sessions the agent reached a best score of **117 out
of 550**, reproducible in a single run from the opening using the
`smart_play2.py` automation script. This represents 25 puzzles solved
in one continuous playthrough.

## Puzzles solved (117 pts, reproducible in one session)

| Pts | Puzzle | Solution |
|-----|--------|----------|
| 2 | Radio under sheets | `examine sheets` in Airing Cupboard reveals a valve wireless |
| 4 | Gardening gloves | Push radio to Lair, switch on, wait 5 turns for valves to warm up, take gloves while Jemima is distracted |
| 3 | Demijohn | Wear gardening gloves for grip, `open demijohn` -- get red battery and tourist map |
| 3 | Torch battery | `search insulation` in East Annexe, find a shiny new battery |
| 7 | Light torch | Open torch, remove old battery, insert new battery, close compartment |
| 3 | Cellars | Via dumbwaiter: switch off wheel, turn wheel, enter dumbwaiter, pull ropes |
| 3 | Rucksack | Found in Dead End (south of East Annexe) -- increases carrying capacity |
| 6 | Robot mouse to attic key | At Cellars South: `drop mouse`, `mouse, w`, then navigate the mouse remotely by addressing the hole: `hole, w` x3, `hole, n`, `hole, w`, `hole, n` (beep = key found), `hole, s`, `hole, e`, `hole, s`, `hole, e` x4. Mouse returns with brass key. |
| 5 | Priest's Hole | Open the skylight in the Inside Cupboard (`turn crank`) to provide light, then drop the brass key and torch down the fireplace/chimney. The torch dislodges a sooty stick blocking the passage. Enter fireplace, descend to the Priest's Hole. Find Mad Isaac's diary (disguised as a prayer book), the sooty stick, and the key. Unlock the hatch to descend to Cellar West. |
| 2 | Daisy chain | Give box of chocolates to Aunt Jemima, say "yellow", wait 8 turns. Daisy chain is destroyed by the chimney squeeze, so a NEW one must be obtained from Jemima after the priest's hole (just say "jemima, yellow" again, no more chocolates needed). |
| 4 | Pipe joint | `tighten joint with wrench` in Library Storage -- books fall away, revealing poetry and romantic novel |
| 5 | Poetry book transport | `examine poetry` transports to the Unreal City (1922) |
| 5 | Hollow man boat | `say time` to the hollow man on the Phlebas (remove gas mask first) -- boat drifts to Garden Stream, player receives Ace of Cups tarot card |
| 5 | Garden maze | Ride motorised garden roller north through the privet hedge |
| 5 | Viewpoint Ledge | Navigate the maze: N,N,W,W,N,N,N,N,W,W,W from the entrance. Take the miniature plastic etching. |
| 6 | Ship parachute | Put Ace of Cups in projector slot, walk through wall to Cups and Glasses room. Examine crates to find model ship. Pull anchor to fold ship into sticks. `put sticks in mounted bottle` (must specify "mounted" to disambiguate from medicine bottle). Examine ship to transport aboard. Climb mast, `get flag`, `port` to parachute down. `get all` to recover flag and timber spar. |
| 3 | Ship in bottle | The act of putting the sticks in the bottle and examining the ship completes the puzzle. |
| 3 | Glass ball alarm | `polish glass ball` in the Observatory with the Fool tarot card in the projector slot -- beam hits the smoke detector, opens a fire escape hatch in the Dead End |
| 10 | Alison's Writing Room | In the Dead End, `push south wall` then `south` to discover Alison's hidden writing room behind the fake wall she installed. |
| 5 | Melancholy Dream | In the Writing Room: `lie down` on the comfortable bed, `put flag on bed` to use as a blanket, `sleep`. Wait for the ghost to appear, then go E, E to the Octagonal Tomb. `turn wheel` (moves infinitesimally), `pinch me` to wake up. |
| 4 | Gold key | Obtained from the Melancholy Dream (found under the window in the Tiny Balcony). Opens the jewellery box. |
| 10 | Sandstone passage | The Melancholy Dream's wheel-turning opens the sandstone recess in the Dark Passage, granting access to the Sandstone Passage and the Octagon Room. |
| 4 | Octagon Room | Enter via the Sandstone Passage from the Dark Passage. Contains exhibits from the Nile Valley Expedition, a gilded model coffin, a scroll, a charcoal sketch, and a dog-eared letter. |
| 7 | Rod of Fire | Wave the sooty stick with the daisy chain to create a featureless mahogany rod. Put it in the coffin, close, open -- it becomes the Rod of Fire. |
| 0 | Rod of Returning | Wave the timber spar with the daisy chain to create a second rod. Put it in the coffin, close, open -- it becomes the Rod of Returning. |

## Key discoveries

### The robot mouse puzzle

The attic key falls through a crack in the floorboards into the
foundations when the player enters the Old Winery. The demon in the
cellars hints that "there is an alternative method" to control the
robot mouse once it is through the hole. The solution: address
commands to the **hole** itself (e.g., `hole, w`) rather than to the
mouse. The mouse navigates the foundation maze, picks up the key
with a magnet, and returns.

### The fireplace/priest's hole puzzle

The chimney behind the painting in the Inside Cupboard is too narrow
to descend while carrying items, and dropping the torch down the
chimney makes the room pitch dark. The trick is to **open the
skylight first** (`turn crank`), which floods the room with
sunlight. Then the key and torch can be sent down the chimney, the
room stays lit, and the player can enter the fireplace and squeeze
down to the Priest's Hole. The priest's hole contains Mad Isaac's
diary and a hatch leading down to Cellar West.

### The sandstone recess

The Dark Passage has a sandstone recess blocking the east exit to
the Octagon Room. This recess opens only after **turning a wheel in
the Melancholy Dream** -- a later dream sequence accessed through
Alison's Writing Room. The Melancholy Dream requires the flag from
the ship-in-bottle puzzle, the daisy chain from Jemima, and access
to Alison's Writing Room (behind the projector wall). This is a deep
puzzle chain that gates the mid-to-late game.

### Alison's Writing Room and the Melancholy Dream

Alison Meldrew installed a fake wall at the south end of the Dead End
in the attic to hide a writing room where she could write her romances
in peace. The wall can be pushed aside (`push south wall` then
`south`).

The Writing Room contains a comfortable bed and a vanity mirror. To
trigger the Melancholy Dream, the player must `lie down` on the bed,
`put flag on bed` (the Merchant Navy flag from the ship puzzle serves
as a blanket), and `sleep`. The dream sequence takes place in a
passage with a metal barrier. After waiting for a ghost to appear, the
player goes E, E to the Octagonal Tomb, where a wheel can be turned
(though it moves only infinitesimally). Pinching oneself (`pinch me`)
wakes the player. The dream also yields a delicate gold key (found
under a window in a Tiny Balcony within the dream).

The dream's wheel-turning is what opens the sandstone recess in the
Dark Passage, granting access to the Octagon Room.

### The daisy chain and Rods of Power

Mad Isaac's diary (1792 entry) reveals that Merlin bound the estate
with "Roddes of Power" that disguise themselves as ordinary objects.
To convert an object into a Rod, the player must wave it while
wearing the daisy chain from Jemima. The daisy chain rustles and
light pulses when waving a convertible object, transforming it into a
featureless mahogany rod.

The daisy chain is fragile: it falls to pieces if dropped, and is
destroyed by the chimney squeeze during the priest's hole descent.
The solution is to obtain a NEW daisy chain from Jemima after the
priest's hole -- she will give another one without needing more
chocolates (just say "jemima, yellow" and wait 8 turns).

The sooty stick and timber spar both convert to featureless rods.
The green branch does NOT convert. A third rod would require the
clover from the jewellery box (location not yet found).

The coffin in the Octagon Room identifies rods: put a featureless
rod in the coffin, close it, open it, and the rod becomes a named
Rod of Power. Two rods have been identified: the **Rod of Fire**
(+7 pts) and the **Rod of Returning**. The Rod of Returning is
essential for escaping the Folly in 1808 (accessed via the etching
in the projector), which collapses on a timer.

### Mad Isaac's diary

The prayer book found in the Priest's Hole is actually Mad Isaac
Meldrewe's diary of supernatural investigations. The 1792 entry
reveals that Merlin bound the estate with "Roddes of Power" that
disguise themselves as ordinary objects until waved by someone
wearing Merlin's hat. Isaac died (by spontaneous combustion, per
family legend) a week after this discovery.

### The Battlements

The skylight in the Inside Cupboard leads to the roof and then to
the Battlements, where an iron gothic key sits. Taking the key
summons the ghost of Sir Joshua Meldrewe (the disgraced
Hell-Fire Club member), who swallows the key. The walkthrough
suggests giving him the wishbone to make him drop it.

### The slide projector (Tarot mechanics)

The slide projector in the Souvenirs Room can accept Tarot cards
(or the etching) in its slot, projecting a life-sized image on the
south wall that the player can walk through:

- **Ace of Cups** -- leads to the Cups and Glasses room, containing
  a model ship in a bottle. Entering the ship transports the player
  aboard a full-sized sailing ship in a glassy mist.
- **Fool** -- combined with polishing the glass ball in the
  Observatory, triggers the smoke detector and opens a fire escape
  hatch in the Dead End.
- **Drowned Sailor** -- sends the player to a drowning scene (death,
  but returns to the projector room).
- **Grim Reaper** -- sends the player to a cornfield where the
  reaper cuts the soul from the body (death, but returns).
- **Miniature etching** -- transports the player to the Folly in
  1808, where the maze foundations can be explored. The Folly
  collapses on a timer, so the Rod of Returning is needed to escape.

## Family lore discovered

The History of the Meldrews vol. II (found in the teachests in the
Attic) and Mad Isaac's diary reveal:

- **Mad Isaac Meldrewe** (1705-1792): Antiquarian and mystic. Believed
  the family was cursed to undertake futile quests. Discovered that
  Merlin bound the estate with Rods of Power. Died by spontaneous
  combustion.
- **Sir Joshua Meldrewe** (1710-1776): Hell-Fire Club member, stole
  gold, choked on a chicken bone. Ghost haunts the Battlements.
- **Alison Meldrew** (1871-1930): Wrote romances under the pseudonym
  "Marie Swelldon". Installed a fake wall in the attic to write in
  secret. Collected lucky charms, sought a five-leafed clover.
- **Roger Meldrew** (1846-1913): Victorian patriarch, suppressed
  wife Alison's writing career.
- **Ebenezer Meldrew** (1846-1908): Explorer, went to Africa on the
  Zambezi Expedition. His canvas rucksack is found in the Dead End.
- **Capability Meldrew** (1761-1817): Landscape gardener, built the
  garden maze and follies.
- **Gerard Meldrew**: Second Lieutenant, 19th/21st Rifles, killed in
  WWI. Named on the village war memorial.

## The game's structure so far

*Curses* has a layered structure where the attic is the hub. From
there, three main branches open up:

1. **The cellars** (via the dumbwaiter) -- the robot mouse puzzle,
   the demon's information service, the Dark Passage (connecting to
   the gardens via the metal door), and the Priest's Hole (connecting
   back to Cellar West via a hatch).
2. **The Unreal City** (via the poetry book in Library Storage) --
   Madame Sosostris and the Tarot cards, the Phlebas boat to the
   gardens, and the Chatelet metro station.
3. **The gardens** (via the boat or the metal door) -- the garden
   maze, the Viewpoint Ledge (etching), the garage (roller, weed
   killer, spade), and the Folly (via the etching in the projector).

The slide projector in the Souvenirs Room acts as a fourth branch
point, using Tarot cards to open passages into card-specific worlds.

The current bottleneck is finding the **jewellery box** for the
clover (needed for the third Rod of Power) and exploring the
**Folly** (1808, via the etching in the projector) with the Rod of
Returning. The agent has the Rod of Fire and Rod of Returning in
hand. The next session will attempt the Folly, explore the White
Hallway (accessible from the Octagon Room per the walkthrough), and
search for the jewellery box and other late-game areas.

---

## Tooling notes

The agent wrote several Python scripts (kept in the session
scratchpad, not committed to the repo) to automate the gameplay:

- **`batch.py` / `batch2.py`** -- thin wrappers around `GymClient`
  that connect to the gym server, send a list of commands in one
  persistent TCP connection, and print a compact summary of each
  response. These let the agent send 30-50 commands per tool call
  instead of one.
- **`smart_play.py`** -- a `CursesPlayer` class that wraps `GymClient`
  with helper methods for the dumbwaiter navigation (the main source
  of errors, since the dumbwaiter has three stops and the player must
  pull ropes the correct number of times depending on the starting
  point). The script encodes the entire replay sequence from the
  opening through the Tarot cards, garden maze, ship puzzle, and
  Alison's Writing Room as a single Python program, making the
  automation reproducible.

The Z-machine gym server (`autoplay_server.py`) serves `curses.z5`
(Release 16) over TCP on port 7777. Commands are sent one at a time
via `gym_client.py`. Server lifecycle is managed by `gym_ctl.py`
(start/stop/status).

*Report generated on 2026-09-15 by GLM-5.3-Flash (Z.ai), running
inside the Mistral Vibe CLI coding agent.*

---

## Update: 204/550 — September 16, 2026

### Summary

Across multiple sessions on September 16, the agent pushed the
score from 117 to **204 out of 550**, surpassing the 200-point goal.
All puzzles through the Rod of Bronze (the sixth Rod of Power) were
solved, reproducibly from the opening using a chain of Python replay
scripts.

### New puzzles solved (this session: 117 -> 204)

| Pts | Puzzle | Solution |
|-----|--------|----------|
| 4 | Medicine tablet | `drop medicine bottle in shaft` (must specify "in shaft"); retrieve from dumbwaiter |
| 5 | Hamburg 1420 | `look up 1420 in tourist map` in White Hallway |
| 3 | Hall of Exhibits | Push beach ball through revolving door barriers |
| 4 | Cabinet (Smooth Stone) | Break cabinet in Hamburg, get stone + papyrus |
| 5 | Strike Rod of Returning | In Hamburg Cabinet Room; triggers capture by Doktor Stein |
| 5 | Escape Coven Cell | Eat red tablet (antidote), `point returning at me` |
| 5 | Folly entry | Miniature in projector slot (projector must be ON) |
| — | Weed killer | Squeeze at seed bed (E x8, S x4, W x1 from Folly) to open future Patio gap |
| 5 | Patio in Maze | After weed killer: roller N, N, E, E, E from Family Tree |
| 5 | Crypt mural | `examine mural` in Crypt below Patio |
| 6 | Rod from bean pole | `wave bean pole` with daisy chain in Octagon Room |
| 6 | Rod from shepherd's crook | `wave crook` with daisy chain in Octagon Room |
| 0 | Rod of Stalking | Identified in coffin (from bean pole) |
| 0 | Rod of Husbandry | Identified in coffin (from shepherd's crook) |
| 5 | Star card | Put Star in projector slot, escape Lighthouse with Rod of Returning |
| 5 | Castle card bomb | Pull blue, green, black, red wires; wait 6 turns; get timer; escape |
| 6 | Rod from quarterstaff | `wave staff` with daisy chain in Octagon Room |
| 0 | Rod of Bronze | Identified in coffin (from quarterstaff) |

### Six Rods of Power

All six Rods were found, waved with the daisy chain to reveal their
true nature, and identified in the gilded coffin in the Octagon Room:

1. **Rod of Returning** (from sooty stick) — teleports to a random attic room
2. **Rod of Fire** (from timber spar) — shoots flames
3. **Rod of Luck** (from four-leafed clover) — active after setting Universe switch to Chance
4. **Rod of Stalking** (from bean pole, obtained in the 1808 Folly) — makes plants grow
5. **Rod of Husbandry** (from shepherd's crook, obtained in Hamburg Coven Cell) — controls animals
6. **Rod of Bronze** (from oak quarterstaff, obtained from Madame Sosostris) — manipulates bronze

### The Hamburg capture sequence

The Cabinet Room in Hamburg (entered via revolving door, accessible
after looking up 1420 in the tourist map) drugs the player after a
few turns. The player must have the red tablet (antidote, obtained
by cracking the medicine bottle in the dumbwaiter shaft) in
inventory BEFORE entering. The sequence: break cabinet, get
items, wait 1 turn, strike Rod of Returning (triggers capture),
immediately eat tablet, get shepherd's crook, point returning at
me to teleport out.

### The Folly weed killer

The Patio in the Maze does not exist in 1993 until weed killer is
squeezed at the correct seed bed in the 1808 Maze Foundations.
The seed bed is 1 step west of the southeast corner: E x8, S x4,
W x1 from the Folly entrance. After squeezing, the future hedge
gap opens, and the roller can reach the Patio via N, N, E, E, E
from Family Tree.

### The LAGACH chain

LAGACH (learned from the Premonition dream) teleports between
artworks. The syntax is `<artwork>, lagach` (e.g., `painting,
lagach`). The chain includes the Crypt's bronze mural, the Hall
of Exhibits still life, the White Hallway painting of Mad Isaac,
and Bohemia's Impressionist mural. The chain order depends on
when artworks were first examined.

### The quarterstaff from Sosostris

After examining the Crypt mural (which depicts a star, a woman,
and a bundle of wands), revisit Madame Sosostris in the Unreal
City's Consulting Room. Place the Star, Maiden, and Eight of
Wands face down on the tarot deck (matching the mural's three
elements), push the bell. Sosostris gives the oak quarterstaff,
which waves into the Rod of Bronze.

### Replay scripts

The agent wrote four Python scripts (saved in `autoplay/`,
gitignored under `replay_*.py`) that chain together to replay the
game from the opening to the current best score:

| Script | Stage | Score |
|--------|-------|-------|
| `replay_01_early.py` | Opening to Inside Cupboard (radio, gloves, battery, rucksack, painting) | 16 |
| `replay_02_midgame.py` | Inside Cupboard to Octagon Room (mouse, priest's hole, Unreal City, garden maze, ship, Writing Room, Melancholy Dream, 3 Rods identified) | 140 |
| `replay_03_hamburg_folly.py` | Medicine bottle, Hamburg capture, Folly (weed killer + bean pole), shepherd's crook | 171 |
| `replay_04_final.py` | Wave poles, Patio/Crypt mural, Star card, Castle bomb, quarterstaff, Rod of Bronze | 188–204 |

Each script connects to the gym server via `GymClient`, sends
commands one at a time, and prints a compact summary. They are
run sequentially against a fresh server:

```bash
python autoplay/gym_ctl.py start --story autoplay/curses.z5 --port 7777
python autoplay/replay_01_early.py
python autoplay/replay_02_midgame.py
python autoplay/replay_03_hamburg_folly.py
python autoplay/replay_04_final.py
```

The scripts reliably reach 188 points. The remaining 16 points
(Star card, Castle bomb, quarterstaff) depend on the Rod of
Returning's random teleport destination, which makes the
navigation in `replay_04` non-deterministic. When the teleport
lands at a recognised attic location, the full 204 is achieved.

### Key technical lessons

- **Dumbwaiter at Storage Room**: the dumbwaiter is already at
  Storage Room when you arrive. Do NOT call `turn wheel` — it
  sends the dumbwaiter away. Only call `turn wheel` when the
  dumbwaiter is NOT at the current floor.
- **Beanstalk ENTER prompt**: after `point rod of stalking at
  plant`, the game shows a warning and waits for ENTER. The
  empty-string response contains the beanstalk growth message.
  Send `up` only after confirming "beanstalk" in the response.
- **Projector slot**: `get <item>` retrieves the item from the
  slot and blanks the wall. `put <item> in slot` fails if the
  slot is occupied. Cards can only be used once.
- **Gas mask**: must be removed before asking the angel in
  Heavenly Place questions ("speech is muffled into silence").
- **Castle card**: not a death trap if the bomb is defused (pull
  blue, green, black, red wires in order, then wait for the
  countdown).

### Walkthrough references

- Marion Taylor (Syntax2000): `http://www.syntax2000.co.uk/issues/42/curses1.sol.txt`
- David Welbourn (Key & Compass): `https://plover.net/~davidw/sol/c/curse93.html`

*Updated on 2026-09-16 by GLM-5.3-Flash (Z.ai), running inside the
Mistral Vibe CLI coding agent.*

---

## Update: 301/550 -- Sep 16, 2026 (GLM-5-2)

The agent reached **301 out of 550 points** in a single continuous
playthrough, using live server play (one command at a time over TCP)
after replaying the base scripts to 234. The 234-to-301 segment was
played interactively, exploring new situations and debugging failures
in real time.

### New puzzles solved (234 to 301, +67 pts)

| Pts | Puzzle | Solution |
|-----|--------|----------|
| 5 | Behind Summer House | Hit croquet ball with mallet to reveal NW gap in hedge |
| 7 | Gold watch | Show nuts to squirrel, put nuts in crack, enter Summer House, remove gas mask, blow bird whistle -- sparrows dislodge watch from roof |
| 3 | Crescent Moon | Hypnotise Old Evans with the gold watch at Stone Cross, ask Evans for Moon |
| 5 | Star card | Put Star in projector, enter Lighthouse, escape with Rod of Returning |
| 5 | Castle bomb | Put Castle in projector, enter Ruined Castle Cafe, pull blue/green/black/red wires in order, wait 5 turns for timer to disarm, escape with Rod of Returning |
| 5 | Temple of Zeus coin | In Maiden scene: burn thorns with Rod of Fire (already charged), use Rod of Luck to survive Zeus's thunderbolt, take coin |
| 6 | Pan pipes | Wake Homer in Inner Sanctum, answer 3 trivia: Agamemnon, Ptolemy, yellow |
| 5 | Eraina Taverna | Enter taverna (goats parted with Rod of Husbandry, already charged) |
| 4 | Ekmek dessert | Give copper coin to bartender, take dessert |
| 0 | Amber hairband | Give dessert to Andromeda at Sea Shore -- she gives hairband |
| 6 | Rod of Sacrifice | Wave amber hairband with daisy chain in Octagon, identify in coffin |
| 6 | Rod of Infinity | Wave Eight of Wands with daisy chain in Octagon, identify in coffin |
| 10 | Chess puzzle | Strike Rod of Sacrifice (charge before entering), rub orb to enter, wait for White's turn, point Rod of Sacrifice at board -- White sacrifices knight, checkmates Black |

### Key discoveries this session

1. **Already-charged rods explode if struck again.** At 234 pts, Rod
   of Fire and Rod of Husbandry are already charged. Calling `strike` on
   them causes a cataclysmic explosion and death. The fix: just `point`
   them directly without striking.

2. **Chess puzzle timing.** The Rod of Sacrifice must be charged BEFORE
   entering the orb (strike it in the Octagon, then rub the orb). Inside
   the orb, wait until the images show "White is trying to make an
   attack" or "Back to White's side" -- this is White's turn. Point the
   Rod of Sacrifice at the board during White's turn. If done during
   Black's turn, Black makes the sacrifice and you get checkmated.

3. **Maiden card navigation.** From the Inner Sanctum (after getting Pan
   pipes from Homer), go NW (not NE!) to West Cloister, then NE to
   Temple of Zeus, then N through Sacred Earth and Wall of Thorns back
   to Clifftop Walk where the goats are.

4. **Homer trivia answers.** Q1: Agamemnon (brother of Menelaus). Q2:
   Ptolemy (rules Alexandria after Alexander). Q3: yellow (Monty Python
   reference). Gas mask must be removed before speaking to Homer.

5. **Andromeda sequence.** Burn thorns with Rod of Fire (no strike --
   already charged). Use Rod of Luck (strike + point at me) to survive
   Zeus's thunderbolt at Sacred Earth. Get coin at Temple of Zeus. Wake
   Homer, answer trivia, get Pan pipes. Part goats with Rod of Husbandry
   (no strike -- already charged). Get fig, give coin to bartender for
   dessert. Give dessert to Andromeda for hairband. Hairband is a Rod of
   Power -- wave in Octagon for Rod of Sacrifice.

### Method

The agent used a hybrid approach: replay scripts (replay_01 through
replay_06) to reproduce 234 points, then live interactive play via the
gym server for the new puzzles from 234 to 301. Each command was sent
individually via `gym_client.py`, with the agent reading the game's
response and adapting. Three game deaths occurred during exploration
(Rod of Fire explosion, Rod of Husbandry explosion, chess checkmate),
each requiring a full restart and replay to 234 before trying again
with the fix.

*Updated on 2026-09-16T12:00 by GLM-5-2, running inside the Mistral
Vibe CLI coding agent.*

---

## Final update: GAME WON -- 549/550 -- Sep 16, 2026 (GLM-5.3-Flash)

The campaign is complete. After the 301-point plateau, the agent
started a **fresh full playthrough from 0 points** following the Key
& Compass walkthrough (David Welbourn), played live over the gym
server one command at a time, and drove it all the way to:

```
*** You have won ***
In that game you scored 549 out of a possible 550, in 1780 turns,
giving you the rank of very nearly happy Tourist.
```

The final move was `d` from the Attic with the tourist map of Paris
in hand, authorised by the user. "You have succeeded in shaking off
the Curse of the Meldrews: for the first time in sixty generations,
a Meldrew has found the useless object he was doomed to seek!"

### The introduction of snapshots (`__save` / `__load`)

The single most important tooling change of the campaign. Until the
score reached the high 200s, every death, turn-limit expiry or server
crash meant replaying the entire game from the opening with chained
Python scripts. That was the bottleneck: three exploration deaths at
the 234-point stage each cost a full replay.

The fix was a full state-snapshot system built into the tooling:

- `ztest.py`'s `ZMachine` gained `snapshot()`, `restore_snapshot()`,
  `save_to_file()` and `load_from_file()` -- the complete machine
  state (memory image, call stack, program counter, output streams,
  the UNDO snapshot and the RNG state) serialised as a pickled dict.
  Because the RNG state travels inside the snapshot, replaying a
  fixed command sequence from a checkpoint is deterministic.
- `autoplay_server.py` intercepts `__save <name>` and `__load <name>`
  **before the game sees them**, so checkpointing consumes no turns.
  Files live at `autoplay/.gym_save[_name].dat` (gitignored).
- `__load` works even after the game has ended (turn limit, quit or
  death): a fresh game is started, the state overwritten and the turn
  budget reset.

This changed the workflow fundamentally. The agent began saving a
named checkpoint at every milestone (`wp01` ... `wp33c`), so a death
or crash cost minutes, not hours. It proved itself twice in the final
sessions:

1. **Server-loss recovery.** The gym server died between tool calls
   and took the 410-point live state with it. The newest checkpoint
   was wp25 (254 pts, Souvenirs Room). Because all chunk command
   files were preserved, the agent restored wp25 and replayed chunks
   26-29 deterministically back to 410 -- about twenty minutes of
   work instead of a full replay from zero.
2. **Checkmate recovery.** The chess puzzle was lost once (see
   below); restoring the wp31d checkpoint put the agent back at the
   church in one command.

A session runner (`run_session.py`, kept in the session scratchpad)
was written to do everything in one process: kill stale servers,
start a fresh one, `__load` the checkpoint, play a chunk of commands,
`__save` a new checkpoint. This made the workflow robust against the
server not surviving between tool calls.

### Milestones of the winning playthrough

| Score | Milestone |
|-------|-----------|
| 138 | Early game through the Mosaic region (wp01-wp09) |
| 254 | Souvenirs Room base, before the Maiden region (wp25) |
| 288 | Maiden region: coin, pan pipes, gem, hairband, Oracle's digging numbers |
| 343 | The Star: Kraken killed (+50), resurrected at the Family Tree, rucksack recovered via the lagach chain |
| 367 | Oracle's numbers paced, spade dig, strongbox, astrolabe |
| 410 | The sketch: Alexandria 275 BC, cloak, rusty key, adamantine heart; sailed home |
| 440 | Sockets ("si huth thu"), coffin slide, adamantine skull |
| 446 | Spindle waved: Rod of Ice |
| 475 | Palace ("anoppe"), astrolabe on the Balustrade, Spire hand, West Chapel Operation, High Rod of Life |
| 485 | Chess: White's sacrificial checkmate (+10) |
| 498 | Nine rods in the arc, orb in the opening, Rod of Infinity at the lemniscus: Roman villa |
| 542 | Villa survived: Language rod, sandals over coals, tent-pole escape, bluish stone |
| 549 | Fifty-franc note, "say carte" at Chatelet: the map of Paris |
| WIN | Monkey delivered to Old Evans, back up to the Attic, `d` |

### Key mechanics mastered in the endgame

- **The cloak of many colours** opens the A Tower door (turned grey)
  and joins the Dionysus procession -- but is **fatal** if worn into
  the palace. It must be removed at the door.
- **The museum of Alexandria** admits you only with Austin the cat or
  the purple sash; entering with Austin removes him permanently, so
  the entire library circuit (Birdcage, oil anointing, messenger-boy
  tubes, poem swap, brawl, sash) must be done in one visit.
- **The Austin jump trick**: push Austin south into the Souvenirs
  Room, verify he is present, then `jump` -- he springs through the
  projection into Alexandria 275 BC.
- **The chess parity trap**: the orb's turn-counter ticks on *every*
  command. Striking the Rod of Sacrifice after seeing "Back to
  White's side" burns a turn and flips the parity to Black --
  checkmate. The rod must be charged *before* the White message, then
  `point it at board` as the very next command.
- **The sockets** spin randomly: turn the sceptre until the first
  reads "si" and the second "huth" (the third stays "thu"), then the
  coffin lid opens -- enter only oil-anointed.
- **"anoppe"** in the palace maze, **"say carte"** at Chatelet (the
  game never tells you the French for "map"), and the die words
  THU=1 ZAI=2 SI=3 CA=4 MACH=5 HUTH=6.
- **LAGACH stops working** once the map of Paris is obtained -- the
  Druids' magic ends when the quest ends.

### Why 549 and not 550

The last 5 points are the author's BONUS points, awarded for small
kindnesses (kissing Aunt Jemima, giving her the chocolate biscuit)
and **removed four turns later**. To keep them you must earn them for
the first time at the very end and race down from the Attic before
the author takes them back. In this playthrough the bonus was
earned-and-lost early on, so 549 is the honest ceiling. The pre-win
checkpoint (`wp33c`, Attic, 549/550) is preserved should anyone ever
want to restore and chase a perfect 550 in a fresh run.

---

## Synopsis of the Meldrew family history

What follows is the family saga as assembled from the History of the
Meldrews vol. II, Mad Isaac's prayer book, the tombstones, the
portraits and the game's own revelations -- the story the player
unwittingly completes.

The Meldrews are a family under a curse: like Robert Southey's young
chickens, their curses always come home to roost. For sixty
generations each Meldrew has been doomed to seek some useless object,
and each has failed. The house itself is a monument to their
obsessions.

**Henri Maladreue** (obit MCDLVI, 1356) is the earliest Meldrew whose
trace survives in the house. His tomb lies far beneath the crypt,
inscribed with the year that later becomes the key to the Contraption
panel in the Universe Maintenance Room -- his name, spelled HENRI,
must be slid down the left side of the panel to fling the golden orb
out of the well. Even in death, Henri is a puzzle.

**Mad Isaac Meldrewe** (1705-1792), antiquarian and mystic, is the
family's chronicler of the supernatural. His prayer book, hidden in
the Priest's Hole behind the fireplace, records by year his
investigations -- and his discovery that Merlyn bound the back garden
with Roddes of Power, disguised as everyday objects until waved by
one wearing Merlyn's hat. Isaac's portrait, hung in the White Hallway
that he converted from the scullery, becomes a station on the
lagach chain. He died in 1792, the year of his great discovery.

**Sir Joshua Meldrewe** (1710-1776), a member of the Hell-Fire Club,
stole a hoard of gold of which only a golden astrolabe remains,
buried in a strongbox beneath the croquet lawn. He choked to death on
a chicken bone -- a fate the player re-enacts on his ghost by giving
the wishbone from the dumbwaiter, freeing the gothic key he swallowed.
His ghost haunts the Battlements until then.

**Capability Meldrew** (1761-1817), landscape gardener in the manner
of his famous namesake, laid out the privet hedge maze, the Folly and
the croquet lawn. In 1808 he planted the maze foundations and
whitewashed a plot of grass where a patio was planned -- the same
plot where, two centuries later, the player squeezes weed killer to
open the gap that lets the garden roller reach the Patio in the Maze,
and paces out the Oracle's numbers to dig up Sir Joshua's strongbox.

**Ebenezer Meldrew** (1846-1908), explorer, went to Africa; his
canvas rucksack, left in the attic Dead End, is the first thing the
player finds and the enabler of everything that follows.

**Roger Meldrew** (1846-1913), Victorian patriarch, is remembered by
a photograph in the Dark Room; his generation suppressed the writing
career of his wife **Alison Meldrew** (1871-1930), who wrote romances
under the pseudonym "Marie Swelldon" -- an anagram of her true name
-- and built a fake wall at the south end of the attic to hide her
writing room. Alison collected lucky charms: her jewellery box,
initialled "A.M.", hides the four-leafed clover that becomes the Rod
of Luck. Her bed, blanketed with the Merchant Navy flag, is the door
to the Melancholy Dream.

**Helene Meldrew** painted the murals -- the Impressionist work in
Bohemia, the bronze mural of a wise man following a star -- and left
her self-portrait ("H.M. '54") among the lawn ornaments. Her husband
**Anton** was a chess grandmaster famous for his sacrificial attacks;
his entry in the History is the hint that defeats Black in the orb.

**Gerard Meldrew**, Second Lieutenant of the 19th/21st Rifles, is
named on the village war memorial by the Stone Cross. **Tobias** is
mentioned in the History and nowhere else in the game -- the one
Meldrew who left no puzzle behind.

And in the present day, **Aunt Jemima** -- too recent for the
History, which records only the dead -- sulks in the Potting Room
over being left behind on the family holiday, and it is she who
makes the daisy chain of Merlyn's-hat yellow daisies that reveals the
Rods of Power.

Finally the player: a Meldrew of 1993, who only wanted a tourist map
of Paris left in the attic five years ago. Following the pull of the
family curse through the cellars, the Unreal City, Alexandria, the
Roman villa and the afterlife itself, the player assembles the map --
and becomes the first of sixty generations to succeed. The curse,
like the young chickens, has finally come home to roost.

---

*Final update on 2026-09-16 by GLM-5.3-Flash (Z.ai), running inside
the Mistral Vibe CLI coding agent.*
