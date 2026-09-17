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
printf 'look\nnorth\nquit\ny\n' | python autoplay/autoplay.py --story autoplay/curses.z5 --max-turns 5 --transcript out.txt
```

### Serve a game as a gym

Use `gym_ctl.py` to manage the server lifecycle. It kills stale
servers before starting, tracks the PID, and waits until the server
is ready:

```bash
# Start a server
python autoplay/gym_ctl.py start --story test_lovecraft.z5 --port 7777 --max-turns 50

# Check if a server is running
python autoplay/gym_ctl.py status

# Stop the server
python autoplay/gym_ctl.py stop
```

`start` kills any existing gym servers (found via PowerShell on
Windows, pgrep on Unix), launches a fresh one in the background, and
blocks until it prints "Listening on". The PID is saved to
`autoplay/.gym_server.pid`.

End the game automatically after N turns of input (useful for bounding
agent sessions) with `--max-turns N`.

The server runs forever (until stopped). It handles one client
connection at a time; a client may disconnect and reconnect without
losing progress. When a client connects after the game ended, a fresh
game starts automatically — no server restart needed.

For turn-by-turn play from a script or agent, use one-shot mode:

```bash
python autoplay/gym_client.py --port 7777 --command "look"
```

### Live play: watch for stale connections

When playing turn-by-turn, connection hygiene matters because game
state is per-server, not per-connection:

- **Before starting**, confirm nothing is already holding the port:
  `gym_ctl.py status`, plus a port check (`netstat -ano | grep :7777`
  on Windows, `ss -ltn` on Unix). A stale server from a previous
  session will silently serve an old game.
- **Never reconnect after `done: true`.** Any connection made after
  the game ended starts a fresh game, so a stray reconnect silently
  resets your progress. Quit explicitly (`quit`), then `gym_ctl.py
  stop`.
- **`TIME_WAIT` sockets after stopping are normal.** Each one-shot
  turn is a connect/disconnect cycle, so a burst of `TIME_WAIT`
  entries on the port is expected residue, not a stuck connection —
  they clear on their own within a minute or two.

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

## Checkpoint / restore (`__save` / `__load`)

The gym server supports two control commands that do NOT consume a
game turn. They snapshot the interpreter's full state (memory, call
stack, PC, RNG) to disk, so a long session can be checkpointed and
resumed — even after the game ended or the server was restarted.

```bash
python autoplay/gym_client.py --port 7777 --command "__save"            # -> autoplay/.gym_save.dat
python autoplay/gym_client.py --port 7777 --command "__save curses277"  # -> autoplay/.gym_save_curses277.dat
python autoplay/gym_client.py --port 7777 --command "__load"            # restore default
python autoplay/gym_client.py --port 7777 --command "__load curses277"  # restore named
```

- `__load` works even when the current game has ended (turn limit,
  quit, death): the server starts a fresh game and overwrites its
  state with the snapshot. The turn budget (`--max-turns`) is reset
  to 0 on load.
- Snapshot files are gitignored (`.gym_save*.dat`). Save at every
  milestone — a lost session otherwise means replaying from the
  replay scripts.
- The game's own in-game `save`/`restore` commands still fail; use
  `__save`/`__load` instead.

### Snapshots and logging go together

A checkpoint without a log is a blind restore: the state survives,
but the knowledge of how you got there and what to do next does not.
Always use the two as a pair:

- **Checkpoint at every milestone** with a meaningful name
  (`__save wp25`), and **record the same milestone in the session
  log** (`autoplay/curses_session_log.md`, gitignored): the score,
  location, what was just done, and the exact command sequence
  (chunk file) that produced it.
- **Keep the command chunks.** When a live state is lost, the
  newest checkpoint plus the preserved chunk files let you replay
  deterministically from the checkpoint (the RNG state travels
  inside the snapshot, so a fixed command sequence reproduces the
  same run). Without the chunks, a checkpoint only tells you where
  you were — not how to move on.
- **Log gotchas as you hit them** (parser names, fatal moves,
  timing traps). A restored session starts with no memory; the log
  is the only memory it has.

This was proven in practice: a server crash lost a 410-point live
state, but the wp25 checkpoint (254 pts) plus the preserved chunk
command files plus the session log allowed a full deterministic
replay back to 410 in minutes. Neither artifact alone would have
sufficed.

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
- The game's own `save`/`restore` return failure. UNDO works. Use the
  gym's `__save`/`__load` control commands for real checkpoints (see
  "Checkpoint / restore" above).
- Single-line input only. `read_char` returns the first character.
- The gym server handles one connection at a time. Game state is
  per-server, not per-connection. Reconnects resume the game; a
  connection after the game ended starts a fresh game.
- A crashed game thread (e.g. an unimplemented opcode) is reported to
  the client as a final `done: true` response containing the
  traceback, not a hang.
- Same compiler quirks as `ztest.py` — see the root
  `Z_TEST_TOOL.md` "Quirks" section.
