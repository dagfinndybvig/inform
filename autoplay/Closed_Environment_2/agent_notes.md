# Agent Notes — Closed_Environment_2 — plant.z5 (Countdown to Doom)

Game: "Countdown to Doom" V1.03, Peter D. Killworth (Inform 6 port).
Planet: Doomawangara. Ship clock: 400 turns. Max score: 325.

## Mission briefing (from restart)

Ship needs within 400 turns:
- dilithium crystals (very dangerous to handle)
- a motor unit
- a navigation unit box
- a life support system
- a medikit
- a nuclear reactor
- plus treasure

Found this run: motor unit (rocky hole), navigation unit box (glacier base).
Nuclear reactor: inside the artefact (unreachable this run — see artefact section).

## Strategy

Systematic exploration with headless gym play (one-shot turns), checkpointing
(`__save <name>`) before every risky area, and restoring on death. Deaths cost
nothing but a restore; the clock only advances on real turns.

## THE BIG BREAKTHROUGH — phaser + glacier end

The phaser gun melts when fired in "normal" cold or heat ("The cooling system
in the ancient phaser isn't too good; the phaser melts in your hand"). It
melts at the glacier BASE, in the desert, at the swamp bottom, in the jungle,
and SW of the artefact.

**But at the END (extremity) of the glacier it works:**

    "It is so cold here that the phaser works fine, and melts the ice wall
    in a trice!"

The colder it gets, the better the phaser works. The vertical ice wall at the
end of the glacier is the target. Firing there does NOT kill you — you survive
("Once in reasonable temperatures again, you soon recover").

Route to the wall: Landing area → `up` (Base of glacier) → `w` (Higher up) →
`w` (End of glacier) → `fire gun`. Cold timer is 4 actions from the base, so
this is exactly the budget. Checkpoint `glacier_open` = wall melted.

## New region west of the glacier (all discovered this session)

    End of glacier --(phaser melts wall)--> What used to be the end of glacier
      → w → Small rocky cave
              ├─ sw → Eastern side of ice-rink → arch (w) → ice-rink (DEATH)
              └─ s  → Bend in the cave → Junction below a high funnel
                        ├─ w  → Small cave burrow → AEROSOL CONTAINER
                        │        └─ sw → allodile (DEATH — eats you)
                        ├─ s  → Small glassy room corridor (4 rooms, switches)
                        └─ ne → back to Bend in the cave

### Ice-rink
"Enormous brown ice-rink" beyond an archway. Stepping on it: you slip, skid,
and your bodily warmth melts the ice — you sink and die. The spacesuit does
NOT insulate. `skate` is not a verb; `run w` dies the same way. Unsolved.

### Allodile
SW of the cave burrow (with "a smell of mud"). Looks like land; stepping on it
prompts "Do you want to carry on?" — answering yes: "He yawns, displaying
eighty-seven teeth. He then ingests you." Key line: "who isn't so **dormant as
his friends are**" — dormant allodiles exist somewhere else. Likely the
swamp-crossing aid (the swamp at the landing area drowns you otherwise).
The aerosol is "too far to reach from here" to spray at it from the burrow.

### Aerosol container
In the small cave burrow (funnel junction, w). Sprays "a rather feeble
dribble" that evaporates. Does not help the ice-rink (sprayed then stepped on
the ice — died anyway). Purpose unknown. Possibly for the allodile or swamp.

### Glassy corridor
South of the funnel junction: a corridor of identical "small glassy rooms",
each with "a large, sturdy switch" on the east wall. Four rooms deep; the
first three switches turn on and STAY on; the fourth "won't move at the
moment". Room 1 says "In the southward direction lie three identical rooms";
the last says "To the north lie three identical rooms". Purpose unknown —
possibly controls the ice-rink, the allodiles, or something else.

## Rest of the map (learned this run)

### Ship
- Control room: ruined console, one functional button (does nothing), some
  explosive with self-igniting fuse.
- Explosive solution: take explosive → cargo hold → drop it → control room →
  `light fuse` → "From next door there is a loud bang!" (you survive) →
  cargo hold `push door` → door falls outward → `ne` to Landing area.

### Landing area (from cargo hold ne)
Exits: swamp NE/N/NW (drown), glacier track `up`, jungle W (randomized maze),
valley S, mountains SE, cliffs path E, ship SW.

### Desert (valley S, S)
Green sand, sandstorm, "compass spinning in a dubious manner", trog-fishing
net. **Fully sealed**: all 8 compass directions give "stagger around,
completely lost"; up/down/in/out fail; sunstroke kills in 3 moves. The net is
unobtainable usefully. `dig` works but "nothing buried on the planet".

### Swamp (landing area NE)
Drowns instantly — UNLESS wearing the decrepit spacesuit: its oxygen works
and you sink safely to the **Bottom of the swamp** (firm ground, natural
luminescence). But the bottom is another randomized maze ("stagger around,
completely lost" in every direction incl. diagonals) and the oxygen gives out
after ~3 moves, killing you. No items found there.

### Glacier (landing area `up`)
Base → Higher up (E/W) → End of glacier (east passage loops back to Higher
up; vertical ice wall west). Cold kills in 4 actions from the base; the
spacesuit does NOT protect against cold. The phaser melts the ice wall (see
breakthrough above).

### Volcano (mountain pass `up`)
Slugs drop from the sky and kill instantly. The phaser doesn't help (carried
or fired); wearing the spacesuit makes it WORSE ("They surround the flimsy
material of your spacesuit, tear it apart"). No protection found.

### Mountain pass area
S → L-bend (N back to pass, E → Box canyon dead end with carved hint "Write
steep, read flat" — slides are walkable). Slide W down → Valley (avalanche
but survivable). NW → Landing area.

### Burnt ground (cliffs path E)
Rocky hole (motor unit on antigrav platform, `pull lever` = +2 points,
platform+motor follow you; platform power is move-based, dies permanently,
lever then does nothing). Metallic cube S ("only partly exists", walls blur;
inside is empty, only exit N; other directions rejected). Jelly blob
(electrified, kills on touch; falls into the swamp on arrival). Paths NE
(→ artefact dome), E (→ three-way junction), SW (→ landing area). `west` from
burnt ground is blocked; return via SW.

### Three-way junction
N dead end: phaser gun. S dead end. W back to burnt ground. Disturbing the
metatermites sends them south; they later turn up in the cargo hold
("ravenous", nothing constructive can be done to them).

### Artefact (NE of burnt ground) — AVOIDED per instructions
Grey metallic dome, tunnel entrance NE (glows blue, rejects the phaser:
"thrown out again"). Entry chamber → curving metal corridor loop of 4
segments, each with a niche (hexagon/pentagon/triangle/square) — all lead
into the tube maze (the trap from run 1). Entry chamber has NO exit back
outside. The whole artefact is a one-way trap. Dome wall SE has an unexplained
anagram: `sedlrazieoyzstbftaholobet`.

### Jungle (landing area W)
Large randomized maze of identical rooms ("completely disorienting").
Escapable by repeated moves; nothing found in ~30 moves.

## Items and what they do

- **Phaser gun** (three-way junction N dead end): melts when fired everywhere
  EXCEPT the end of the glacier, where it melts the ice wall. One shot only.
- **Spacesuit** (crevasse east end, worn): provides oxygen in the swamp (lets
  you reach the bottom). Does NOT protect against cold, heat, or slugs.
- **Aerosol container** (cave burrow): feeble dribble, purpose unknown.
- **Navigator box** (glacier base): mission item; "box is a technical term
  used by space navigators to mean - er - a thingy".
- **Motor unit** (rocky hole): mission item; far too heavy to carry; rides the
  antigrav platform.
- **Antigrav platform**: `pull lever` = +2 points, follows you, dies after
  ~5-6 moves permanently.
- **Explosive + fuse** (control room): blasts the cargo hold door.
- **Trog-fishing net** (desert): unobtainable usefully (desert is sealed).

## Hazards and their timers

| Area | Killer | Budget |
|---|---|---|
| Desert | sunstroke | 3 moves |
| Swamp bottom | oxygen runs out | ~3 moves |
| Glacier | cold | 4 actions from base |
| Ice-rink | body warmth melts ice | instant |
| Volcano | slugs | instant |
| Allodile | eaten | instant |
| Jelly blob | electrocution | instant |

## Parser facts

- `verbose` mode helps spot special rooms in mazes.
- Death prompt: `undo` works once; a bare `look` at the death prompt can
  replay the death. `restart` → "Would you like the story so far?" `no`.
- `__save`/`__load` do not consume turns; saves taken in the same bash call as
  a move capture the pre-move state.
- The game discourages examining: "Look, I'm your eyes and hands."
- `dig` is a real verb ("nothing buried on the planet that I know of").
- `fish`, `skate`, `melt` are not verbs. `shoot <scenery>` tries to take it
  ("That's hardly portable").
- Pending yes/no prompts (allodile) can jam one-shot input — restore clean.

## Checkpoints left on disk (gitignored)

- `outside2`, `nav_box`, `desert`, `net`, `suited2`, `pass_suited`, `gun`,
  `gun_landing` (gun+nav box at landing area), `suited_gun` (suit worn + gun +
  nav box), `landing2`, `swamp`, `glacier_open` (wall melted), `cave`,
  `cave_bend`, `funnel`, `aerosol` (burrow, holding aerosol), `glassy`
  (corridor, switch on), `rink_east`, `motor_delivered`, `before_artefact`.

## Unsolved

1. **Ice-rink crossing** — ice melts under body warmth; suit doesn't insulate.
2. **Allodile** — awake here; dormant "friends" somewhere (swamp?).
3. **Aerosol** — purpose unknown.
4. **Glassy corridor switches** — 3 on, 4th stuck; purpose unknown.
5. **Desert** — fully sealed; net unobtainable.
6. **Artefact** — one-way trap; reactor inside; anagram unexplained.
7. **Volcano slugs** — no protection found.
8. Remaining mission items: dilithium crystals, life support system, medikit,
   treasure (and the reactor, inside the artefact).

## Score

2/325 (antigrav lever). Ship clock ~260 remaining at last check.
