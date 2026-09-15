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

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--story PATH` | `adventure_lovecraft.z5` (repo root) | Path to the `.z5` story file |
| `--seed N` | none | Seed for the `random` opcode (deterministic playthrough) |
| `--transcript FILE` | none | Write a transcript of the session to this file |

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
    def __init__(self, *args, transcript=None, story_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.transcript = transcript

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
