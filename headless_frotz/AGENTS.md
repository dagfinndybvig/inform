# AGENTS.md — headless_frotz live play

Quick-rules card for driving `dfrotz.exe` as a live, turn-by-turn
interpreter session (background process + incremental output reads).
The README covers what this directory is and how dfrotz was built; this
file is the recipe an agent must follow in every session.

## The recipe

All four tools live under the `tools.process` namespace:
`tools.process.start`, `tools.process.output`, `tools.process.write`,
`tools.process.stop`.

1. **Start the game** as a background process (`tools.process.start`),
   never as a blocking shell command:

   ```
   command: "./dfrotz.exe -m -q -s 1 STORYFILE"
   cwd:     this directory
   ```

   `-m` (no MORE prompts) and `-q` (quiet) are mandatory for scripted
   play. `-s N` seeds the RNG — always pass it, or runs are not
   reproducible. `-h #` / `-w #` set screen size if needed.

2. **Read the initial output** with an incremental read
   (`tools.process.output`, `from: "end"`, `waitMs: 2000`). The game
   banner, opening room, and the first `>` prompt arrive together.

3. **Send each turn as two writes** (`tools.process.write`):

   - write 1: the command text, **without** any newline
   - write 2: `control: ["enter"]`

   Then read again (`from: "end"`, `waitMs: 2000`). The response
   appears after the echoed command line.

4. **Parse the tail**: each read returns the whole newest output page,
   not just the delta. The newest turn's text is everything after the
   last echoed `>command` line. Status lines (score/moves) mark each
   turn boundary.

5. **Watch the status field.** Every `output` read returns `status` and
   `exitCode`; `status: "completed"` with `exitCode: 0` means the game
   has exited (normal after QUIT). Check it before writing — writing to
   a completed process raises `process_not_running`.

6. **Keep the user updated continuously — this is mandatory, not
   optional.** Never batch a long playthrough silently. Report between
   tool calls: what milestone was just reached, what the score/moves
   are, what the next move is and why. A turn-by-turn account is the
   whole point of live play; a silent run is a failed run even if the
   game is won.

7. **Stop cleanly — and always do it before ending the session.** At a
   game-over or menu prompt, send the menu word (`QUIT`, etc.) + enter
   and let the process exit on its own. To kill a runaway session
   (e.g. stuck waiting for input), use `tools.process.stop` — but note
   it raises `process_not_running` if the game already exited, so guard
   with the status field first.

   **Why this matters:** dfrotz with no `MORE` prompts sits waiting for
   input forever — an abandoned process never exits on its own. Every
   session that forgets to stop leaves an orphaned `dfrotz.exe`
   accumulating in the process list (they show up in later
   `tools.process.list` calls as stale entries), and a live one can
   hold the story or save file open. Verify with `tools.process.list`
   at the end of a session: no `dfrotz.exe` entry should remain
   `running`.

## Save and restore

Proven end-to-end with HHGG (`-s 42`): save at a safe point, die later,
restore, and continue from the exact saved state (score, inventory,
position, and move counter all come back).

- **Save early, save often — this is mandatory, not optional.** Save at
  *every* safe checkpoint: after the opening inventory, after each major
  plot milestone (e.g. the Prosser swap), and always before risky or
  irreversible points — standoffs, point-of-no-return moves, anything
  the game gates on a timer. One `save` costs one turn; dying without
  one costs the whole run. A run that reaches a milestone without a
  save has not banked it.
- **`save` is a line-input prompt.** The game asks
  `Please enter a filename [STORYFILE.qzl]:` — send a bare
  `control: ["enter"]` to accept the default. The `.qzl` file is written
  in this directory (the cwd of the dfrotz process).
- **On death, RESTORE, don't RESTART.** At the
  `(Type RESTART, RESTORE, or QUIT): >` menu, send `RESTORE` + enter,
  then a bare enter for the default filename. With the same `-s` seed a
  restore is a checkpoint, not a reroll — you land exactly where you
  saved.
- **A restore does not change the future.** The seed makes the timeline
  deterministic: the same events fire at the same move counts (HHGG:
  Vogon ships at move 50, Earth destroyed at 53). If the saved position
  is already doomed, restoring just replays the doom — change the
  strategy *before* the gate, then save at the new safe point.
- **Never commit `.qzl` files.** `.gitignore` covers `*.z3`/`*.z5` but
  not `*.qzl` — add `headless_frotz/*.qzl` before committing anything
  from this directory.

## Walkthroughs and cheats

- **Do not use walkthroughs, Invisiclues, web solutions, or any other
  cheats unless absolutely required — and ask the user first.** Solve
  puzzles by playing: observe the room descriptions, experiment, and
  reason from what the game tells you. External help is a last resort
  for a hard blocker, never a default. If a puzzle stalls after genuine
  attempts, stop and ask the user whether to consult a walkthrough
  before fetching one. When the user approves, cite what was taken from
  it in the session report (e.g. PROGRESS.md).

## Gotchas

- **A bare `\n` inside the command text is NOT an Enter.** Under the
  conpty the game never sees it; the command just sits at the prompt
  unexecuted. Always send `control: ["enter"]` as a separate write.
  (Piped input, by contrast, works fine with `\n` — the difference is
  pipe vs pseudo-console.)
- **Reads race the echo.** Reading immediately after the write often
  returns only the echoed command with no response. Wait and read
  again; use `waitMs` so the read blocks until output arrives.
- **dfrotz emits conpty escape sequences** (`\x1b[13;2H`, cursor
  addressing around echoes, a burst at startup). Ignore them; the game
  text between them is clean plain text.
- **`from: "end"` returns a full page, not a delta.** Don't re-parse
  the whole history every turn; slice from the last prompt marker.
  Pages are capped (~30 KB); for very long sessions check `hasMore` /
  `truncatedBefore` and read forward from `nextCursor` if needed.
- **Line-input prompts consume a whole command.** Prompts like
  "(Hit RETURN or ENTER when ready.)" eat the next line you send — a
  queued command will be swallowed by them. Send a bare enter (or a
  throwaway line) for such prompts and re-issue the real command after.
- **Game timers are real.** HHGG's bulldozer demolishes the house after
  ~20 moves. Don't burn turns retrying an action the game is gating.
- **Seed-dependent gating**: HHGG's hangover spinning blocks every
  action (including walking) until it randomly lifts; with `-s 1` it
  never lifted within the timer. A different seed changes it. When a
  game seems impossibly stuck, suspect the seed before suspecting the
  setup.
- **The move counter can jump.** In HHGG, once the bulldozer halts each
  `wait` advances the move counter by 3 while other commands advance 1.
  Timed events therefore arrive sooner (in commands) than the move
  numbers suggest — plan countdowns in commands, not moves.

## Files

- `dfrotz.exe` — the interpreter (Frotz 2.55 dumb interface; see README)
- Story files (`.z3`/`.z5`) live here but are gitignored — never commit
  them (Infocom games are copyrighted).
