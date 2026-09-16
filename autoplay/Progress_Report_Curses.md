# Progress Report: Playing Curses

This report summarises the progress of an AI agent playing Graham
Nelson's *Curses* (1993) using the Z-machine gym server in this
repo's `autoplay/` folder. The game is played one command at a time
over TCP, with no save/restore -- each session replays from the
opening.

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
