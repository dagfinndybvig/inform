<img width="1024" height="768" alt="Curses3" src="https://github.com/user-attachments/assets/921e66eb-ffbe-430b-b3a4-d0734b124723" />

# autoplay/ — Play and Serve Z-machine Games

This folder contains tools for playing Z-machine text-adventure games
headlessly — without a graphical interpreter — and for turning any game
into an interactive environment that an AI agent can explore.

## What is the Z-machine?

The Z-machine is a virtual machine designed in 1979 to run Infocom text
adventures. A game is compiled to a `.z5` file (Z-machine version 5),
which contains all the rooms, objects, rules, and text of the game
world. An interpreter loads the file and runs it, reading player commands
and printing descriptions of what the player sees and what happens.

This repo includes its own Z-machine interpreter written from scratch in
Python (`ztest.py` in the repo root), so no external software is needed.

## What is a "world-gym"?

A gym is a controlled environment where an agent — a human, a script, or
an AI like an LLM — can interact with a simulated world one step at a
time. The agent sends a command ("look", "take key", "go north"),
receives the result (room descriptions, object responses, score
changes), decides what to do next, and continues until the game ends.

This is different from pre-scripting a fixed sequence of commands. The
agent can explore blindly: it doesn't need to know the game in advance.
It reads the output, reasons about what it sees, and picks the next
action — exactly how a human plays.

## Tools in this folder

### autoplay.py — Interactive terminal player

Plays any `.z5` game in the terminal. Output appears as the game
produces it; you type commands at the `>` prompt. Supports
`--transcript` to record the session to a file with a game-info header,
and `--max-turns N` to stop after a fixed number of input turns.

```bash
python autoplay/autoplay.py --story archive/adventure.z5
```

See [`Z_AUTOPLAY_TOOL.md`](Z_AUTOPLAY_TOOL.md) for full documentation.

### autoplay_server.py — Gym server

Runs a `.z5` game as a TCP server. An external agent connects, sends
one command at a time, and receives the game's response after each
command as structured JSON (output text and a done flag). Supports
`--max-turns N` to end the game after a fixed number of input turns.
Clients may disconnect and reconnect without losing progress; when a
client connects after the game ended, a fresh game starts
automatically.

Use `gym_ctl.py` to manage the server lifecycle:

```bash
python autoplay/gym_ctl.py start --story test_lovecraft.z5 --port 7777
python autoplay/gym_ctl.py status
python autoplay/gym_ctl.py stop
```

See [`Z_AUTOPLAY_GYM.md`](Z_AUTOPLAY_GYM.md) for the protocol, API, and
architecture.

### gym_client.py — Client library and CLI

Connects to the gym server. Can be used interactively from the
terminal, one command per invocation (for turn-by-turn play from a
script), or imported as a Python library for programmatic play.

```bash
# interactive
python autoplay/gym_client.py --port 7777

# one command per invocation; game state persists on the server
python autoplay/gym_client.py --port 7777 --command "look"
```

```python
# library
from gym_client import GymClient

client = GymClient(port=7777)
client.connect()
opening = client.recv()
print(opening["output"])

resp = client.send("take key")
if resp.get("error"):
    print("Server error:", resp["error"])
print(resp["output"])
print("score:", resp["score"])
```

## Why model worlds as Z-machine games?

The Z-machine is a general-purpose world simulator. The "adventure"
framing is just one skin. An `.inf` source file can define any set of
interconnected rooms with objects, containers, doors, NPCs, timers, and
state machines. The game compiles to `.z5`, and the gym serves it.

This means you can model anything:

- **An industrial plant** — rooms are zones, objects are valves and
  gauges, the player is an operator doing a safety walkthrough. Score
  for completing the procedure in the right order.
- **A building evacuation** — rooms are floors and hallways, doors lock
  and unlock, fire spreads via timers, the player must find exits and
  guide people out.
- **A guided tour or onboarding** — rooms are stations, objects are
  equipment, examining things teaches the player how they work.

The agent doesn't need to know the world in advance. It connects to the
gym, reads the opening description, explores, examines objects, opens
doors, and builds a mental model of the world — turn by turn, exactly
like a person arriving somewhere new. You score the agent on whether it
completed the objective: did it finish the safety checklist, evacuate
everyone, find and fix the bug?

The infrastructure already exists. Writing a new `.inf` file is the only
creative work needed to create a new world.
