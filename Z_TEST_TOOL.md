# ztest.py — Headless Z-machine v5 Interpreter

`ztest.py` is a from-scratch Z-machine v5 interpreter written in Python. It
loads a `.z5` story file, feeds it a scripted list of commands at each `aread`
(input) call, and prints all screen (stream-1) output to stdout. It exists
because the only local Z-machine interpreter (Frotz) is a GUI-only Windows
executable that cannot be driven from a pipe, making automated regression
testing of gameplay impossible.

## What code it works on

`ztest.py` lives in the `inform/` project directory and defaults to
`adventure_lovecraft.z5` (the compiled game for *The Goddess in the Cellar*).
For local testing after a code change, compile to `test_lovecraft.z5` and pass
it with `--story` instead (see [Workflow](#workflow) below). It can run any
Z-machine v5 story file via `--story`:

```bash
python ztest.py --story adventure.z5 "look" "quit"
python ztest.py --story adventure_lovecraft.z5 "look" "score" "quit"
```

It does **not** work on Z-machine v1–v4 or v6 story files — the packed-address
multiplier (`*4`), property-table format, and routine encoding are v5-specific.
It also assumes the local Inform 6.44 compiler's non-standard routine format
(see "Quirks" below).

## Usage

```bash
# inline commands
python ztest.py "look" "take notebook" "n" "score" "quit" "y"

# from a script file (one command per line, # = comment)
python ztest.py --script test_commands.txt

# mix both
python ztest.py --script setup.txt "take flower" "eat flower" "score"

# mark each command in the output with a ###CMD: header
python ztest.py --mark "look" "score" "quit" "y"

# deterministic randomness
python ztest.py --seed 1 "look" "quit" "y"

# interactive (reads from stdin, Ctrl-Z to end)
python ztest.py
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--story PATH` | `adventure_lovecraft.z5` | Path to the `.z5` story file |
| `--script FILE` | none | File of commands, one per line (`#` = comment, blank lines skipped) |
| `--seed N` | none | Seed for the `random` opcode (deterministic playthrough) |
| `--mark` | off | Print `###CMD: <command>` before each command's output |
| `commands...` | none | Inline commands, executed in order |

When the game calls `quit`, it prints "Are you sure you want to quit?" and
expects a follow-up command — typically `"y"`. Include `"y"` as the last
command in your list to confirm and exit cleanly.

### `--mark` output format

With `--mark`, each command is preceded by a marker line so you can parse
output per-action:

```
###CMD: take notebook
Taken.
[The score has just gone up by four points.]
```

This is useful for grep-based assertions in regression scripts.

## Example session

A scoring regression test — take the key, travel to the Stone Circle and
navigate the labyrinth to the Altar Chamber, unlock the ornate box, take and
eat the flower, then check the score:

```bash
python ztest.py --mark --seed 1 \
  "take key" "n" "e" "n" "n" "e" "n" "n" \
  "unlock ornate box with rusty key" \
  "open ornate box" \
  "take flower" \
  "eat flower" \
  "score"
```

Output (relevant lines):

```
###CMD: take key
Taken.
[The score has just gone up by four points.]
###CMD: n
[The score has just gone up by five points.]
###CMD: e
[The score has just gone up by five points.]
###CMD: n
###CMD: n
###CMD: e
###CMD: n
###CMD: n
###CMD: unlock ornate box with rusty key
You unlock the ornate box.
###CMD: open ornate box
You open the ornate box, revealing a blue flower.
###CMD: take flower
Taken.
[The score has just gone up by four points.]
###CMD: eat flower
You bite into the bloom, and its viscous nectar floods your mouth with a taste
at once sweet and profoundly wrong -- a flavor that seems to resonate in
chambers of your mind that were never meant to open. The petals dissolve upon
your tongue like ash, and for a moment the garden's crooked geometry seems to
swim and right itself. You sense, with a certainty beyond all reason, that
your lungs have been quietly remade to endure an atmosphere not of this earth.
[The score has just gone up by ten points.]
###CMD: score
You have so far scored 28 out of a possible 80, in 12 turns.
```

Score breakdown: key (+4) + Garden (+5) + Forest (+5) + flower (+4) + eat
flower milestone (+10) = **28 out of 80**, in 12 turns. The Stone Circle and
all labyrinth rooms have no `scored` attribute, so they award no points. This
matches the scoring design documented in `README.md` exactly.

## What it implements

The interpreter covers the full instruction set the game uses:

- **2OP, 1OP, 0OP, VAR, and EXT (0xBE) opcode forms**, including the v5
  extended opcodes (`save_undo`, `restore_undo`, `log_shift`, `art_shift`,
  `print_unicode`, `check_unicode`, `set_font`).
- **Call/return**: `call_vs`, `call_vn`, `call_2s`, `call_2n`, `call_1s`,
  `call_1n`, `call_vs2`, `call_vn2`, `ret`, `ret_popped`, `rtrue`, `rfalse`.
- **Branching**: all branch forms (short 1-byte, long 2-byte, `rtrue`/`rfalse`
  on offset 0/1).
- **Object tree**: `insert_obj`, `remove_obj`, `get_parent`/`sibling`/`child`,
  `test_attr`/`set_attr`/`clear_attr`, `jin`.
- **Properties**: `get_prop`, `get_prop_addr`, `get_prop_len`, `get_next_prop`,
  `put_prop`, with correct v5 one-byte and two-byte property encoding.
- **Text**: z-string decoding (alphabets A0/A1/A2, abbreviations, 10-bit
  ZSCII escape), `print`, `print_ret`, `print_char`, `print_num`,
  `print_paddr`, `print_addr`, `print_obj`, `new_line`, `print_table`.
- **Dictionary**: binary-search dictionary lookup with proper z-character
  encoding (9 z-chars / 6 bytes per entry, v5).
- **Input**: `aread` (tokenizes the next scripted command into the text and
  parse buffers), `read_char` (returns newline).
- **Memory**: `loadw`/`loadb`/`storew`/`storeb`, `copy_table`, `scan_table`.
- **Output streams**: stream 1 (screen, captured to stdout) and stream 3
  (memory tables, for `print_to_buf`-style routines). Screen, window, cursor,
  and text-style opcodes are no-ops.
- **Undo**: `save_undo` / `restore_undo` with full state snapshot (memory,
  stack, call frames, PC). Follows the Inform convention: fresh save returns
  `1`, restored save "returns" `2`.
- **Random**: `random` opcode with optional `--seed` for deterministic runs.

Screen/window opcodes (`split_window`, `set_window`, `set_cursor`,
`set_text_style`, `erase_window`, `buffer_mode`, `set_colour`,
`draw_picture`, `sound_effect`) are no-ops — the output is plain text.

## Quirks

Two non-standard behaviors of the local Inform 6.44 build required specific
handling:

1. **No local initial-value words in routines.** The Z-machine standard
   specifies `[nlocals byte][nlocals words of init values][code]`. This
   compiler emits `[nlocals byte][code]` with all locals starting at 0 — no
   init-value words. This was confirmed by compiling a minimal test program
   and inspecting the output. The interpreter skips init-value reading.

2. **v5 packed-address multiplier is `*4`**, and byte addresses can exceed
   `0xFFFF` (the story file is 0x16000 bytes). Address arithmetic must not be
   masked to 16 bits. The interpreter uses `*4` for routine addresses,
   `print_paddr` string addresses, and abbreviation addresses.

These mean `ztest.py` will **not** correctly run story files compiled by
standard-compliant Inform 6 builds that emit local init-value words — it would
misinterpret them as code. For this project's compiler, it works.

## Workflow

The intended workflow for regression-testing after a code change:

1. Edit `adventure_lovecraft.inf`.
2. Recompile to the local test build (not the canonical file):
   ```bash
   ./inform6_compiler/inform6.exe +inform6lib/inform6lib-master adventure_lovecraft.inf test_lovecraft.z5
   ```
3. Run a test playthrough against the test build:
   ```bash
   python ztest.py --mark --seed 1 --story test_lovecraft.z5 "look" "take key" "n" "e" "score" "quit" "y"
   ```
4. Check the output for expected responses, score changes, and absence of
   library errors.

For repeatable test suites, keep command lists in `.txt` files under version
control and run them with `--script`:

```bash
python ztest.py --mark --seed 1 --story test_lovecraft.z5 --script tests/scoring.txt > tests/scoring.out
```

Then `diff` against a known-good baseline.
