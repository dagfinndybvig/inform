# Report: Exploring Curses with the Z-machine Gym

This report covers three things: the game and its author, the gym
system this repo uses to let an AI agent play text adventures, and a
20-turn exploration session of *Curses* that focused on one puzzle —
getting the tourist map out of the demijohn.

## Graham Nelson, Inform, and Curses

Graham Nelson is a British mathematician and programmer who wrote
*Curses* in 1993. He is also the author of the Inform compiler — the
programming language this repo uses to build text adventures. In the
interactive fiction community he is something of a founding figure:
Inform, and the library that comes with it, were developed alongside
*Curses*, and the game doubled as the compiler's showcase.

*Curses* is old school in the classic Infocom sense. The player wakes
in the attic of a cluttered ancestral house in 1993, looking for a
tourist map of Paris, and gradually uncovers a family history that
stretches back through a cursed bloodline to the fall of Troy. The
game is famous for its scale (a maximum score of 550 points), its
literary epigraphs, and its puzzle design: nothing can be solved with
what you start carrying, obvious approaches are politely closed off,
and the game expects you to wander, examine, and get stuck before the
pieces fit together.

One example met head-on in this session: the game opens with a
hinged trapdoor leading down out of the attic. Going down it does not
open the game up — it ends it immediately, with the message
"*** You have missed the point entirely ***". Leaving the attic
before understanding why you are there counts as giving up.

## The gym system, for the layman

A text adventure is a program that reads short commands ("take key",
"open demijohn") and prints what happens. To play one, you normally
sit at a keyboard. The question this repo's `autoplay/` folder answers
is: how does an AI agent play one?

The answer is the **gym** — a small server program built on top of the
repo's own Z-machine interpreter (`ztest.py`, a from-scratch Python
implementation of the 1979 Infocom virtual machine). The gym takes any
compiled story file (`.z5`) and serves it over a network connection:

1. The gym server loads the game and waits for a client.
2. A client connects and sends one command as a line of JSON:
   `{"cmd": "open demijohn"}`.
3. The server feeds the command to the game, collects everything the
   game prints in response, and sends it back as JSON — together with
   the turn number, the score, and whether the game has ended.
4. The client reads the response, decides what to do next, and sends
   the next command. Repeat until the game ends.

This is a "gym" in the machine-learning sense: a controlled
environment where an agent takes one step at a time, observes the
result, and decides the next step — exactly how a human plays, except
the keyboard has been replaced by a network protocol.

Two recent additions made the session in this report possible:

- **The game state lives on the server, not the connection.** A client
  can disconnect and reconnect without losing progress. This means an
  agent can play one command per invocation — start the server once,
  then send a single command, read the result, think, and send the
  next one. No pre-scripted command list, no replaying from the
  beginning to try a different move.
- **One-shot client mode.** `gym_client.py --command "open demijohn"`
  connects, sends that one command, prints the response, and exits.
  Twenty turns of play become twenty short commands, each answered
  before the next is chosen.

When the game ends, the server automatically starts a fresh game for
the next client, so the same server can be reused for repeated
sessions.

## The session: 20 turns hunting the map

The session was played blind — the agent (me) knew nothing about
*Curses* in advance beyond the opening text, and chose each command
after reading the previous response. The goal was deliberately narrow:
the game's own to-do list says "1. Find map", so the session focused
on finding the tourist map.

### What was found

- **The start.** The player is in the Attic of the family house,
  carrying a chocolate biscuit, an electric torch, and a crumpled
  piece of paper. The paper reads: "Things to do: 1. Find map. 2.
  Phone airport to check parking. 3. Health forms... Let's face it,
  1. is more enticing than the rest put together."
- **Three attic rooms explored.** The Attic itself; the Servant's Room
  to the east (a bed, a little book, and an old striped scarf); and
  the Old Winery to the north.
- **The map, located but not reached.** In the Old Winery stands a
  labelled glass demijohn — a large wine jar — which is closed, and
  inside it are a nasty-looking red battery and the tourist map.
- **A setback.** Entering the Old Winery disturbs the still air and
  knocks the attic key off the demijohn, down through a crack in the
  floorboards. Recovering it is another problem for later.
- **A clue.** The demijohn's faded label reads "Elderberry '63". The
  scarf, once examined, is a Biblioll College scarf with four stripes:
  royal blue, emerald, dark grey and scarlet — colours that look like
  they matter to a different puzzle.

### What was tried, and why it failed

The demijohn is the obstacle between the agent and the map. Twenty
turns of approaches, all refused:

| Attempt | Response |
|---------|----------|
| `open demijohn` (bare hands) | "Your hands slip on the screw-top of the demijohn and can't get a grip." |
| `open demijohn` holding the scarf | Same slip. |
| `open demijohn` wearing the scarf | Same slip. |
| `open demijohn with scarf` | "That doesn't seem to be something you can unlock." |
| `tie scarf to demijohn` | "You would achieve nothing by this." |
| `turn demijohn` / `unscrew demijohn` | "It is fixed in place." |
| `break demijohn` | "The demijohn is made of something like industrial-grade chemistry glass. You kick it and hurt your foot." |
| `examine top` | "You can't see any such thing." (no separate screw-top object) |

Every brute-force approach is explicitly closed off — typical Nelson
design. The real solution presumably needs an object not yet found.
The house below the trapdoor and the attic's southeast continuation
(Old Furniture) are the obvious next hunting grounds.

### How the session ran

The gym server was started once in the background with `curses.z5`.
Each turn was a single one-shot client call; the response was read
before the next command was chosen. The game state persisted on the
server throughout, so the twenty commands formed one continuous game —
no replays, no lost progress. The session ended at turn 20 in the Old
Winery, score 0, game still in progress.

A small bonus: the gym's startup routine, which identifies the game's
score and turn counters by playing the game to itself, successfully
detected them for *Curses* — so the score and turn fields in the
protocol were live during the session, not just the text output.

## Summary

Twenty turns was enough to map a third of the attic, locate the map,
and establish that the demijohn cannot be opened by force, by hand,
or by scarf. The session is a small demonstration of the gym's
purpose: an agent walking into a game it has never seen, reading,
reasoning, and getting stuck exactly where a human player would —
one command at a time.
