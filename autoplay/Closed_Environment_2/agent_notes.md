# Agent notes — blind run of plant.z5 ("Countdown to Doom")

## Outcome

Mission failed. Final score 2 out of 325 (the antigrav-platform lever). The
ship corroded away at turn 401 twice; both deaths happened while trapped
inside the artefact's tube maze. The run ended with the maze unsolved.

## What was accomplished

- Explored the surface: landing area, valley, desert edge, jungle maze,
  burnt ground, cliffs, three-way junction, artefact dome.
- Retrieved the motor unit from the rocky hole using the antigrav platform
  (pull lever, +2) and delivered it to the cargo hold.
- Found 4 glass discs (pentagon, square, hexagon, triangle) in the artefact's
  tube maze; located the store room, cramped cubicle (nuclear reactor), and
  the screen-of-light room in the pre-restart game.
- Mapped the ship's collapse clock (400 turns) and the warning messages.

## Strategy

Started with systematic surface exploration, prioritizing obvious item
locations. Used the ship's mission briefing as the item checklist. Treated
the artefact as the endgame and entered it late, after securing the motor.
Checkpointed at every milestone (`__save`) and kept the transcript current.

## Dead ends

1. **The explosive in the control room** is a death trap if handled wrong;
   the light-fuse-drop-run-south sequence works but wastes turns.
2. **Desert sunstroke** kills without protection; never solved.
3. **The electrified jelly blob** kills on touch; never solved.
4. **The screen of light** kills unconditionally when crossed — tried
   empty-handed, loaded, waiting, timing, and every robot interaction
   (push, talk, attack, ride). The robot steals one item per turn and stolen
   items are unrecoverable.
5. **The artefact tube maze (the run-killer).** ~320 tube moves across
   multiple 78-turn checkpoint windows with varied move patterns. Findings:
   - Only `left/forward/right/back` move the tubes; the compass is useless.
   - The maze behaves as random (or one-way tubes): `back` does not reliably
     reverse, and identical moves from identical rooms give different results.
   - Roof holes are unreachable by any verb (`enter hole`, `up`, `climb`,
     `jump`, throwing discs). The game states the hole is "far too high".
   - The discs do nothing: carrying all 4, carrying only the square one
     (the corridor niche was marked SQUARE), inserting them into tubes or
     the hole, and dropping them in a room all change nothing.
   - The floor-hole room (down to the store room, hence the reactor) never
     appeared in this game's maze, though it existed pre-restart. The disc
     room appeared roughly a third of the time, suggesting a small room pool
     that excludes it.
   - The parser actively discourages examination ("I'll tell you what's
     necessary"), and `dig`, `push tube`, `pull tube`, `out`, `exit` all fail.

## What I learned from the world's feedback

- The game telegraphs its clock ("Time before ship collapse is N") and
  escalates with ship-surface descriptions — time management matters more
  than thoroughness.
- The parser is opinionated and helpful: it suggests verb forms ("just say
  'throw jar'") and rejects impossible actions with specific messages. When
  it says "no way to reach it", it means it.
- The artefact appears to be a one-way trap as played: entering through the
  niche drops you into a maze whose exits do not reconnect to the corridor.
  Either there is a trick I never found (likely something to do with the
  discs or an item that boosts height, e.g. the antigrav platform, which
  cannot follow through tubes), or the intended route is via the floor-hole
  room, which this game's maze never offered.
- Checkpoint discipline (`__save` at milestones plus a session log) saved
  the run twice; a restore also silently undid an item pickup, so
  checkpoints must be taken immediately after state changes.

## If someone retries

Get the antigrav platform BEFORE entering the artefact and keep it following;
it is the only plausible way to reach "too high" holes. Do not enter the
artefact without a confirmed exit plan, and treat the 400-turn clock as the
real budget: surface items first, artefact last.
