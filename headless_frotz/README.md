# headless_frotz

An attempt to get a spec-complete, pipe-drivable Z-machine interpreter
(`dfrotz`-style) working on this Windows machine, to complement — and
possibly replace — the home-grown `ztest.py` interpreter in the repo root.

## Why

- The only local Frotz is `../frotz/Frotz.exe`, a GUI app that cannot be
  driven from a pipe. This is the documented reason `ztest.py` exists.
- `ztest.py` is a from-scratch Z-machine **v5-only** interpreter, married
  to the local Inform 6.44 build (it relies on that compiler's
  non-standard routine headers, which omit local initial-value words).
  It cannot run spec-conformant story files, including v3 games.
- A real Frotz would be spec-complete across v3–v8 and battle-tested.

## The problem

No C compiler exists on this system (no gcc, clang, MSVC, zig), so
building upstream `dfrotz` from source is not currently possible. The
workaround attempted here: a prebuilt **Win32 Console** build of Frotz
2.32 (`WinFrotzConsole/WinFrotz.exe`, Rich Lawrence's WinFrotz 1.08,
downloaded from the if-archive) driven through a pseudo-console.

## Approach

`wfrotz.py` wraps the console Frotz in three layers:

1. **pywinpty** — runs WinFrotz.exe inside a pseudo-console. WinFrotz
   queries the console size at startup and dies with "Fatal Error!" if
   it does not like the answer, so the explicit `-h <rows> -w <cols>`
   switches are mandatory.
2. **pyte** — a terminal emulator that maintains the 50x100 (or larger)
   screen state. WinFrotz's raw output is full of ANSI cursor-position
   sequences (status-line redraws); raw capture is unusable, so the
   screen is rendered to plain text.
3. **Turn driver** — waits for the screen to stabilise on a fresh `>`
   prompt, sends each command (with `\r` only — `\n` is delivered as a
   second Enter and produces "I beg your pardon?"), then prints the
   rendered screen from the echoed command line to the bottom.

Usage:

    python wfrotz.py --story STORY.z5 [--rows 50] [--cols 100] "cmd1" "cmd2" ...

Commands come from positional args or stdin (one per line, `#` comments).

## Findings so far

- Screen size is the make-or-break parameter: without `-h/-w` WinFrotz
  aborts under the pty.
- `\r\n` input is delivered as two Enters; only `\r` works.
- The echoed command line (e.g. `>examine note`) is used as the marker
  for incremental output. Matching must be exact (`>e` must not match a
  stale `>examine note`), and the scan must run from the bottom of the
  screen, since old turns remain visible until they scroll off.
- Short and medium sessions work cleanly: commands execute, output is
  readable, score changes are visible.
- **Known defect**: on long runs (the full 39-command win path at 50
  rows) WinFrotz repaints its virtual screen constantly (~3.5 MB of
  redraw traffic for ~50 KB of game text) and the pyte model drifts —
  the rendered view shows early-game content while the game state
  remains correct. The final `score` output was not captured.
- Working hypothesis for the defect: at 50 rows the game text scrolls,
  and WinFrotz's repaints interact badly with the emulator's scroll
  model. A pty has no real resolution limit, so a much taller screen
  (e.g. `-h 300`) should let the whole game fit without scrolling.
  That test was interrupted mid-run and has not completed yet.

## Motivation

The immediate target is `hitchhiker-r59-s851108.z3` (Infocom's v3
Hitchhiker's Guide) — a spec-conformant v3 story file that `ztest.py`
cannot load. WinFrotz 2.32 runs v3 natively, so the wrapper only needs
to be reliable, not version-aware.

## Alternatives, if this proves too fragile

- Build real `dfrotz` from source (needs a compiler installed — e.g.
  winlibs GCC or MSYS2). dfrotz reads stdin and writes plain text
  natively; no pty, no emulation, no drift. This is the robust
  end state if the pty approach keeps diverging.
- Extend `ztest.py` to v3 (~100–150 lines of version-conditional
  changes; see the repo discussion). Full control, but new maintenance
  burden and it would still not be spec-complete for v4–v8 quirks.

## Files

- `wfrotz.py` — the wrapper (the only real artifact here)
- `WinFrotzConsole/` — unpacked WinFrotz 1.08 distribution (Frotz 2.32
  core, console build) with its bundled ADVENT.Z5 / FREEFALL.Z5 demos.
  Not committed (binaries + story files); download it from
  https://www.ifarchive.org/if-archive/infocom/interpreters/frotz/WinFrotzConsole108.zip
  and unpack into this directory.
- `*.txt` / `*.err` — scratch output from verification runs; safe to
  delete
