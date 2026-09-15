# AGENTS.md — autoplay/ Agent Guide

Quick-rules card for agents (human or AI) working with the autoplay
tools. The README in this folder is the plain-language overview; this
file is the operational how-to.

## What this folder is for

Three tools, one shared design:

- `autoplay.py` — play a `.z5` game in the terminal (one human, one
  session).
- `autoplay_server.py` — serve a `.z5` game over TCP so an agent can
  play it one command at a time (world-gym).
- `gym_client.py` — connect to the gym server, interactively or as a
  library.

All three subclass `ZMachine` from `ztest.py` in the repo root. The
only thing that differs between them is where `next_command` gets its
input. Do not duplicate Z-machine logic here — fix it in `ztest.py`.

## Git workflow

This folder is part of the main repo. Follow the root `AGENTS.md`:

- `git pull --rebase origin main` before starting and before pushing.
- Never commit `.z5` files. CI handles the canonical build.
- `test_lovecraft.z5` is gitignored — it is a local throwaway build.

## Running the tools

All commands assume the repo root as the working directory.

### Play a game in the terminal

```bash
python autoplay/autoplay.py --story test_lovecraft.z5
```

Pipe commands for non-interactive use:

```bash
printf 'look\ntake key\nquit\ny\n' | python autoplay/autoplay.py --story archive/adventure.z5
```

Record a transcript:

```bash
python autoplay/autoplay.py --story archive/adventure.z5 --transcript playthru.txt
```

Limit to N turns of input (useful for bounded exploration):

```bash
printf 'look\nnorth\nquit\ny\n' | python autoplay/autoplay.py --story curses.z5 --max-turns 5 --transcript out.txt
```

### Serve a game as a gym

```bash
python autoplay/autoplay_server.py --story test_lovecraft.z5 --port 7777
```

End the game automatically after N turns of input (useful for bounding
agent sessions):

```bash
python autoplay/autoplay_server.py --story test_lovecraft.z5 --port 7777 --max-turns 50
```

The server runs forever (until Ctrl-C). It handles one client
connection at a time; a client may disconnect and reconnect without
losing progress. When a client connects after the game ended, a fresh
game starts automatically — no server restart needed.

For turn-by-turn play from a script or agent, use one-shot mode:

```bash
python autoplay/gym_client.py --port 7777 --command "look"
```

### Connect a client to the gym

```bash
python autoplay/gym_client.py --port 7777
```

Or as a library:

```python
import sys
sys.path.insert(0, "autoplay")
from gym_client import GymClient

client = GymClient(port=7777)
client.connect()
resp = client.recv()          # opening text
resp = client.send("look")   # one command, one response
print(resp["output"])
print("done:", resp["done"])
client.close()
```

### Run the end-to-end test

```bash
python autoplay/test_gym.py
```

Starts the server, plays both `archive/adventure.z5` and
`test_lovecraft.z5` through the client, verifies the Lovecraft win
output contains `*** You have won ***` and score 90/90, and shuts down.

### Run the demo

```bash
python autoplay/demo_gym.py
```

Starts the server on port 7799, plays 5 turns of the Lovecraft game
interactively, prints output with the done flag per turn, and
shuts down.

## Gym protocol

Newline-delimited JSON over TCP.

Send: `{"cmd": "take key"}`
Recv: `{"output": "Taken.", "done": false}`

Malformed requests get `{"error": "..."}` with `output` empty and the
game state unchanged; the connection stays open.

The first response after connecting is the game's opening text with
`done: false`. No command is needed to get it — just `recv()`.

When `done: true`, the game is over. The server does not report
score, turn count, or win/death state — parse the game's text output
for those (e.g. search for "*** You have won ***"). The connection
can be closed.

## Modifying the tools

- **Do not fork Z-machine logic.** Fix opcode bugs in `ztest.py`, not
  in `autoplay.py` or `autoplay_server.py`. These tools only override
  `next_command` and output routing.
- **Keep `next_command` simple.** It should return a string (the
  command) or `None` (game ends). All blocking, flushing, and queue
  logic belongs in the tool, not in the base class.
- **Use `wait_for_server` in scripts that spawn the server.** It lives
  in `gym_client.py`, reads the server's stderr until it reports
  ready, and fails fast on timeout — never use a blind `sleep` to wait
  for startup.
- **Test after changes.** Run `python autoplay/test_gym.py` to verify
  the gym still works end-to-end. Run the regression test from the
  root `AGENTS.md` to verify the game itself is unaffected.

## Limitations to keep in mind

- No screen formatting, sound, or pictures — all no-ops.
- No disk save/restore — `save`/`restore` return failure. UNDO works.
- Single-line input only. `read_char` returns the first character.
- The gym server handles one connection at a time. Game state is
  per-server, not per-connection. Reconnects resume the game; a
  connection after the game ended starts a fresh game.
- A crashed game thread (e.g. an unimplemented opcode) is reported to
  the client as a final `done: true` response containing the
  traceback, not a hang.
- Same compiler quirks as `ztest.py` — see the root
  `Z_TEST_TOOL.md` "Quirks" section.
