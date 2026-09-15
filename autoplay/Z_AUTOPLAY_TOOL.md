# autoplay.py — Interactive Headless Z-machine v5 Interpreter

`autoplay.py` is a thin wrapper around `ztest.py` that turns the headless
Z-machine v5 interpreter into an interactive terminal player. Instead of
feeding a pre-scripted command list, it reads commands one at a time from
stdin at each `aread` (input) prompt, flushing game output to stdout between
turns. It can play any Z-machine v5 story file that `ztest.py` supports.

## What code it works on

`autoplay.py` lives in the `autoplay/` subdirectory of the `inform/` project.
It imports `ZMachine` from `ztest.py` in the repo root and subclasses it,
overriding a single method (`next_command`) to read from `input()` instead
of a pre-fed list. All opcode implementations, quirks, and limitations are
inherited from `ztest.py` — see [`Z_TEST_TOOL.md`](../Z_TEST_TOOL.md) for
the full list of supported opcodes and known quirks.

It works on any Z-machine v5 story file. It does **not** work on v1–v4 or
v6 files, and it inherits the local Inform 6.44 compiler's non-standard
routine format assumption (no local init-value words).

## Usage

```bash
# play the default game (adventure_lovecraft.z5 in repo root)
python autoplay/autoplay.py

# play a specific story file
python autoplay/autoplay.py --story archive/adventure.z5

# play a local test build
python autoplay/autoplay.py --story test_lovecraft.z5

# seed the PRNG for reproducible random output
python autoplay/autoplay.py --story test_lovecraft.z5 --seed 42

# record a transcript to a file
python autoplay/autoplay.py --story archive/adventure.z5 --transcript playthru.txt
```

You can also pipe commands in for non-interactive use:

```bash
printf 'take key\nlook\nnorth\nquit\ny\n' | python autoplay/autoplay.py --story archive/adventure.z5
```

Use `--max-turns N` to stop after a fixed number of input turns, which is
useful for bounded exploration or testing:

```bash
printf 'look\nnorth\nquit\ny\n' | python autoplay/autoplay.py --story autoplay/curses.z5 --max-turns 5 --transcript out.txt
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--story PATH` | `adventure_lovecraft.z5` (repo root) | Path to the `.z5` story file |
| `--seed N` | none | Seed for the `random` opcode (deterministic playthrough) |
| `--transcript FILE` | none | Write a transcript of the session to this file |
| `--max-turns N` | none | Stop after N turns of input (each `aread` counts as one turn) |

## Example session

```
$ python autoplay/autoplay.py --story archive/adventure.z5

Welcome to The Little Adventure! You are a traveler seeking shelter.


The Little Adventure
A tiny Inform 6 example game
Release 1 / Serial number 240910 / Inform v6.31 Library 6/11 S

Cottage
You are in a cozy cottage. A warm fire crackles in the hearth. There is a
wooden door leading north to the garden, and a narrow stairway going down
to a cellar.

A rusty key lies on the floor near the hearth.

A brass lantern sits on a shelf.

>take key
Taken.

>take lantern
Taken.

>north

Garden
You stand in a small garden. Flowers bloom along a stone path. The cottage
is to the south. A dark forest lies to the east.

A single blue flower grows beside the path.

>quit
Are you sure you want to quit?
>
```

Type commands at the `>` prompt. Press Ctrl-D (or Ctrl-Z on Windows) to
end input. When the game calls `quit`, it asks "Are you sure you want to
quit?" — type `y` to confirm.

## Transcript

Use `--transcript FILE` to record the session. The transcript file begins
with a header extracted from the story file's Z-machine header (filename,
Z-machine version, release number, serial code, recording date, and seed
if set), followed by a separator line and then the full game output with
interleaved `>` prompts — exactly what appears on screen.

Example transcript header:

```
Transcript of adventure.z5
Z-machine v5, Release 1, Serial 240910
Recorded: 2026-09-15 11:22:35
========================================

```

The game's own banner (title, headline, release line) follows immediately
after the header, so the transcript captures the game name and description
without needing to parse it separately.

## How it works

`autoplay.py` subclasses `ZMachine` and overrides `next_command`:

```python
class InteractiveZMachine(ZMachine):
    def __init__(self, *args, transcript=None, story_path=None,
                 max_turns=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.transcript = transcript
        self.max_turns = max_turns
        self.turn_count = 0

    def _write(self, text):
        sys.stdout.write(text)
        if self.transcript is not None:
            self.transcript.write(text)

    def _flush_output(self):
        if self.out_buf:
            text = "".join(self.out_buf)
            self._write(text)
            if not text.endswith("\n"):
                self._write("\n")
            sys.stdout.flush()
            self.out_buf.clear()

    def next_command(self):
        self._flush_output()
        self.turn_count += 1
        if self.max_turns is not None and self.turn_count > self.max_turns:
            self._write("\n[Turn limit reached after %d turns.]\n"
                        % self.max_turns)
            self.running = False
            return None
        try:
            return input(">")
        except EOFError:
            self.running = False
            return None
```

When `--transcript` is set, a header is written to the file before the
game starts. During play, `_write` tees output to both stdout and the
transcript file.

The base `run()` method is a simple `while self.running: self.step()` loop.
When the game hits an `aread` opcode, it calls `next_command()` to get the
player's input. The override flushes any buffered output to stdout, prints
a `>` prompt, and reads one line from stdin. The game then tokenizes and
processes that line, producing more output for the next turn.

No save/restore is needed — the `ZMachine` instance holds all state
(memory, stack, call frames, PC) in memory for the duration of the process.

## Limitations

- **No screen formatting.** Window, cursor, text-style, and color opcodes
  are no-ops. Output is plain text.
- **No sound or pictures.** Sound and picture opcodes are no-ops.
- **No save/restore to disk.** The `save` and `restore` opcodes return
  failure (0). In-game `save_undo`/`restore_undo` (used by UNDO) works.
- **Single-line input only.** Each `aread` reads exactly one line from
  stdin. Key-character input (`read_char`) returns the first character.
- **Same compiler quirks as ztest.py.** See the "Quirks" section of
  [`Z_TEST_TOOL.md`](../Z_TEST_TOOL.md).

## Z-machine header fields

`read_header` extracts metadata from the story file's binary header.
The Z-machine v5 header is a fixed-layout region at the start of the
`.z5` file:

| Offset | Size | Field | Value read |
|--------|------|-------|-------------|
| `0x00` | 1 byte | Version | `5` (Z-machine v5) |
| `0x02` | 2 bytes | Release number | Big-endian word, e.g. `2` |
| `0x12` | 6 bytes | Serial code | ASCII string, e.g. `240916` |

These fields are used to construct the transcript header and are
also available to the gym server for startup logging. The game's
title and headline are not in the header — they are printed by the
game's own code at startup and appear in the game output stream.

Other header fields used by the underlying `ZMachine` (in `ztest.py`)
but not read by `autoplay.py` directly:

| Offset | Size | Field | Used for |
|--------|------|-------|----------|
| `0x04` | 2 bytes | High memory mark | `high_mem` |
| `0x06` | 2 bytes | Initial PC | `initial_pc` (entry point) |
| `0x08` | 2 bytes | Dictionary address | `dict_addr` (word lookup) |
| `0x0A` | 2 bytes | Object table address | `obj_table` |
| `0x0C` | 2 bytes | Globals table address | `globals` |
| `0x0E` | 2 bytes | Static memory mark | `static_mem` |
| `0x18` | 2 bytes | Abbreviations table | `abbrev_table` (z-string decoding) |

## How `aread` works

The Z-machine `aread` opcode (VAR form, opcode 4) is the input
primitive. When the game wants player input, it executes `aread`,
which:

1. Reads a line of text from the player (via `next_command`).
2. Stores the text in the text buffer at the address given by operand
   1. In v5, byte 0 of the buffer is the max chars, byte 1 is set to
   the actual length, and the text follows from byte 2.
3. Tokenizes the text into the parse buffer at the address given by
   operand 2, using the game's dictionary for word separation and
   lookup.
4. Returns a store value of 10 (newline terminator) to the game.

In `ztest.py`, `aread` calls `self.next_command()` to get the input
line. `autoplay.py` overrides this method to read from `input()`
instead of a pre-fed list. The gym server (`autoplay_server.py`)
overrides it again to block on a thread-safe queue until the client
sends a command.

## Transcript format

When `--transcript FILE` is set, a header is written before the game
starts:

```
Transcript of <basename>
Z-machine v<version>, Release <release>, Serial <serial>
Recorded: <YYYY-MM-DD HH:MM:SS>
[Seed: <N>]
========================================

```

The body is a verbatim copy of all game output written to stream 1
(the screen), including the `>` prompt markers. The prompt is injected
by `_flush_output` — it adds a newline if the game output doesn't end
with one before printing `>`. This ensures the prompt always sits on
its own line.

The transcript file is opened in UTF-8 encoding and closed after the
game ends (either by `Quit` exception or EOF on stdin).

## Relationship to the gym server

`autoplay.py` and `autoplay_server.py` share the same design pattern:
both subclass `ZMachine` and override `next_command` to change the
input source. The difference is where the command comes from:

| Tool | Input source | Output destination | Use case |
|------|-------------|-------------------|----------|
| `ztest.py` | Pre-fed command list | stdout (batch) | Regression testing |
| `autoplay.py` | `input()` (stdin) | stdout + transcript file | Interactive terminal play |
| `autoplay_server.py` | Thread-safe queue (from TCP client) | JSON over TCP | Agent-driven play (world-gym) |

All three inherit the same opcode implementations from the `ZMachine`
base class. The only per-tool code is the `next_command` override and
the output routing logic.

The gym server also supports `--max-turns N`, which ends the game at
the next input request after N commands execute — the same semantics
as `autoplay.py`'s turn limit above. Its game state persists across
client connections, and `gym_client.py --command "look"` sends one
command per invocation, giving turn-by-turn play from a script without
holding a connection open.
