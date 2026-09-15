# Progress Report: Playing Curses

This report summarises the progress of an AI agent playing Graham
Nelson's *Curses* (1993) using the Z-machine gym server in this
repo's `autoplay/` folder. The game is played one command at a time
over TCP, with no save/restore -- each session replays from the
opening.

## Sessions and score

Across multiple sessions the agent reached a best score of **27 out
of 550**. A further 31 points from earlier sessions (pipe joint,
poetry book, Phlebas boat, garden maze, Viewpoint Ledge, ship in a
bottle, glass ball) are repeatable but require replaying from scratch
each session because the game state does not persist between server
restarts.

## Puzzles solved (27 pts, reproducible in one session)

| Pts | Puzzle | Solution |
|-----|--------|----------|
| 2 | Radio under sheets | `examine sheets` in Airing Cupboard reveals a valve wireless |
| 4 | Gardening gloves | Push radio to Lair, switch on, wait 5 turns for valves to warm up, take gloves while Jemima is distracted |
| 3 | Demijohn | Wear gardening gloves for grip, `open demijohn` -- get red battery and tourist map |
| 3 | Torch battery | `search insulation` in East Annexe, find a shiny new battery |
| 7 | Light torch | Open torch, remove old battery, insert new battery, close compartment |
| 3 | Cellars | Via dumbwaiter: switch off wheel, turn wheel, enter dumbwaiter, pull ropes |
| 3 | Rucksack | Found in Dead End (south of East Annexe) -- increases carrying capacity |
| 6 | Robot mouse to attic key | At Cellars South: `drop mouse`, `mouse, w` (squeezes through hole), then navigate the mouse remotely by addressing the hole: `hole, w` x3, `hole, n`, `hole, w`, `hole, n` (beep = key found), `hole, s`, `hole, e`, `hole, s`, `hole, e` x4. Mouse returns with brass key. |
| 5 | Priest's Hole | Open the skylight in the Inside Cupboard (`turn crank`) to provide light, then drop the brass key and torch down the fireplace/chimney. The torch dislodges a sooty stick blocking the passage. Enter fireplace, descend to the Priest's Hole. Find Mad Isaac's diary (disguised as a prayer book), the sooty stick, and the key. Unlock the hatch to descend to Cellar West. |

## Additional puzzles solved in earlier sessions (not yet combined into one run)

| Pts | Puzzle | Solution |
|-----|--------|----------|
| 4 | Pipe joint | `tighten joint with wrench` in Library Storage |
| 5 | Poetry book transport | `examine poetry` transports to the Unreal City (1922) |
| 5 | Hollow man boat | `say time` to the hollow man on the Phlebas (remove gas mask first) |
| 5 | Garden maze | Ride motorised garden roller north through the privet hedge |
| 5 | Viewpoint Ledge | Navigate the maze: N,N,W,W,N,N,N,N,W,W,W from the entrance |
| 6 | Ship parachute | On the ship mast: `get flag`, then `port` -- flag becomes a parachute |
| 3 | Ship in bottle | `put sticks in bottle` in the Cups and Glasses room (inside the Ace of Cups tarot card, accessed via the slide projector) |
| 3 | Glass ball alarm | `polish glass ball` in the Observatory with the Fool tarot card in the projector slot -- beam hits the smoke detector, opens the fire escape |

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

The current bottleneck is the sandstone recess, which requires the
Melancholy Dream to open. The next session will focus on completing
the mid-game chain: daisy chain from Jemima, Tarot cards, ship
puzzle, fire escape, Alison's Writing Room, and finally the
Melancholy Dream.

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
