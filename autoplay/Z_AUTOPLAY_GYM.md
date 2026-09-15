# Z-machine Gym — Text-Adventure Environment for Agents

The Z-machine gym turns a `.z5` story file into a TCP server that an
external agent (human, script, or LLM) can play one command at a time.
Unlike `autoplay.py` (interactive terminal) or `ztest.py` (pre-scripted
commands), the gym lets a client send a command, read the response,
decide, and continue — enabling genuine blind exploration of unknown
games.

## Architecture

```
  Client (agent)                  Server
  ┌──────────┐    TCP/JSON    ┌──────────────────┐
  │ gym_client│ ←───────────→ │ autoplay_server   │
  │  .py     │                │   ┌────────────┐  │
  │          │  {"cmd":".."}  │   │ GameThread │  │
  │          │ ──────────→    │   │  ZMachine  │  │
  │          │                │   │  (paused)  │  │
  │          │  {"output":..} │   └────────────┘  │
  └──────────┘ ←───────────    └──────────────────┘
```

- **`autoplay_server.py`** — TCP server that runs the Z-machine in a
  background thread. The game thread pauses at each `aread` (input
  prompt), sends accumulated output to the client, and blocks until the
  client sends the next command. A manager keeps the game alive across
  connections and starts a fresh game when a client connects after the
  previous one ended.
- **`gym_client.py`** — TCP client with both a `GymClient` library class
  and an interactive CLI mode.

## Protocol

Newline-delimited JSON over TCP.

**Request** (client -> server):
```json
{"cmd": "take key"}
```

**Response** (server -> client):
```json
{"output": "Taken.\n", "done": false, "turn": 1, "score": 4, "deadflag": 0}
```

| Field | Description |
|-------|-------------|
| `output` | Game text produced since the last command (room descriptions, responses, prompts) |
| `done` | `true` when the game has ended (quit, win, or death) |
| `turn` | Current turn count (from the game's `turns` global) |
| `score` | Current score (from the game's `score` global) |
| `deadflag` | 0 = in progress, 1 = dead, 2 = won |

The first response after connecting contains the game's opening text
with `done: false` and `turn: 0`. On a reconnect, the cached opening is
resent and the game continues from its current state.

Malformed requests (invalid JSON, or a missing `cmd` field) get an
error response with `output` empty and the game state unchanged:

```json
{"output": "", "done": false, "turn": 0, "score": 0, "deadflag": 0, "error": "invalid JSON"}
```

The connection stays open after an error — the client can simply send
a well-formed command next.

## Usage

### Start the server

```bash
# serve the Lovecraft game
python autoplay/autoplay_server.py --story test_lovecraft.z5 --port 7777

# serve any .z5 file
python autoplay/autoplay_server.py --story archive/adventure.z5 --port 7777
```

### Connect interactively

```bash
python autoplay/gym_client.py --port 7777
```

### Send one command per invocation

For turn-by-turn play from a script or an agent, `--command` connects,
sends one command, prints the response, and exits. The game state
persists between invocations on the server:

```bash
python autoplay/gym_client.py --port 7777 --command "look"
python autoplay/gym_client.py --port 7777 --command "take key"
```

### Use as a library

```python
from gym_client import GymClient

client = GymClient(port=7777)
client.connect()

# Receive opening text
opening = client.recv()
print(opening["output"])

# Send commands and read responses
resp = client.send("look")
if resp.get("error"):
    print("Server error:", resp["error"])
print(resp["output"])
print("score:", resp["score"], "turn:", resp["turn"])

resp = client.send("take key")
print(resp["output"])

# Check if game is over
if resp["done"]:
    print("Game over! deadflag:", resp["deadflag"])

client.close()
```

### Test script

```bash
python autoplay/test_gym.py
```

Runs end-to-end tests on both `archive/adventure.z5` and
`test_lovecraft.z5`, verifying the full win path scores 90/90 with
`deadflag: 2`.

## Server options

| Flag | Default | Description |
|------|---------|-------------|
| `--story PATH` | `adventure_lovecraft.z5` (repo root) | Path to the `.z5` story file |
| `--port N` | 7777 | TCP port to listen on |
| `--host H` | 127.0.0.1 | Host to bind |
| `--seed N` | none | Seed the PRNG for reproducible random output |
| `--max-turns N` | none | End the game after N turns of input (the limit fires at the next input request after N commands execute) |

## How it works

### Game thread

The Z-machine runs in a background `threading.Thread`. Its
`next_command` method is monkey-patched to:

1. Flush the game's `out_buf` into a `result_queue` (visible to the
   socket handler).
2. End the game if `--max-turns` is set and the limit has been reached
   (appends a `[Turn limit reached after N turns.]` message and sets
   `running = False`).
3. Block on `cmd_queue.get()` until the client sends a command.

This lets the game loop run normally (`while self.running: self.step()`)
while pausing at every `aread` for input.

If the Z-machine raises an unexpected exception (for example an
unimplemented opcode on an unusual story file), the game thread catches
it and sends a final `done: true` response containing the traceback, so
the client sees the failure instead of hanging forever.

### Global variable detection

On startup, the server auto-detects which Z-machine global variables
hold `score`, `turns`, and `deadflag` by running two playthroughs of the
game — one win path and one quit path — and comparing which globals
change to expected values (score = 90, turns = 38, deadflag = 2 after
win; all 0 after quit). This is game-specific and works for the
Lovecraft game; for unknown games, detection may fail and these fields
will report 0. The `done` flag always works correctly regardless.

### Limitations

- **One connection at a time.** The server handles one client at a
  time (sequential connections are fine — disconnect and reconnect
  without losing progress). The game state is per-server, not
  per-connection.
- **Reconnect replays the opening.** A reconnecting client is sent the
  cached opening text again, then the game continues from its current
  state.
- **Auto-restart on game over.** When a client connects after the game
  ended, a fresh game starts automatically — no server restart needed.
- **Global detection is game-specific.** The score/turn/deadflag fields
  rely on knowing the win path. For unknown games, use the `done` flag
  and parse score from the game's text output instead.
- **Same Z-machine limitations as ztest.py.** No screen formatting, no
  sound, no disk save/restore. See
  [`Z_TEST_TOOL.md`](../Z_TEST_TOOL.md) for the full list.
