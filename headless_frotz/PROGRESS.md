# Progress Report — Headless Play of The Hitchhiker's Guide to the Galaxy

**Date:** 2026-09-18 16:16 UTC
**Model:** Mistral Vibe (Mistral AI CLI coding agent)
**Setup:** `headless_frotz/dfrotz.exe` (Frotz 2.55 dumb interface, built with
TinyCC), driving `hitchhiker-r59-s851108.z3` as a background process with
incremental output reads. See `README.md` (build) and `AGENTS.md` (recipe).

## Milestone: Earth is escaped — we are aboard the Vogon ship

This session solved the entire Earth act. The run is alive in the Vogon
Hold at score 33 / 400, move 61, with a checkpoint saved
(`hitchhiker-r59-s851108.qzl`, written with an explicit filename after
the overwrite prompt).

## What was played (winning Earth route, seed `-s 42`)

1. **Opening (moves 1–10):** turn on light; get up; take dressing gown;
   wear gown; look in pocket; take analgesic (+10, cures the spinning);
   take screwdriver; take thing.
2. **Standoff (moves 11–18):** south x2; lie down in front of the
   bulldozer; then **wait repeatedly and do nothing else**. Ford arrives
   when the bulldozer halts (~move 14–16). His dialogue tree advances
   one stage per wait: offers towel → "what about my home" → goes for a
   quiet word with Prosser → **Prosser swaps places at ~move 18–20**.
   Taking the towel at this point short-circuits the dialogue and Ford
   leaves — the swap never fires. Patience is the whole puzzle.
3. **Pub (moves ~30–38):** south (Country Lane), west (Pub). Ford buys
   beer. **Drink exactly three beers** — the 4th (in quick succession)
   triggers the drunk ending ("a hangover which lasts for all
   eternity"), and fewer than three leaves you without the muscle
   relaxant. `take towel` works in the Pub even though Ford refuses to
   hand it over if asked.
4. **The end of Earth (moves ~48–53):** keep waiting. The Vogon ships
   arrive (~move 48–50) and the game moves you to Country Lane. Next
   turn Ford drops a small black device; `take device`, then
   **`press green button`** — this is the move that was missing for
   three runs. It teleports you to the Vogon ship *before* the Earth is
   destroyed. Waiting instead of pressing = death at move 53.
5. **The Dark (moves 53–58):** wait four times; each wait drops one
   sense from the "can't" list. When smell returns, `smell` (something
   pungent — Ford waving Santraginean Mineral Water), then
   `smell shadow` → wake in the Vogon Hold. Ford gives peanuts.
6. **Vogon Hold (move 61):** `eat peanuts` (+8, replaces protein lost
   in the beam). Saved here.

## What was learned this session

1. **The Prosser swap is gated on Ford's dialogue tree, not on waiting
   volume.** It fires after ~4 waits post-arrival *if you never take
   the towel first*. The earlier runs (~35 waits, no swap) failed
   because the immediate `take towel` made Ford leave.
2. **The beer dose is exact: three.** 4 quick pints = drunk ending;
   3 = correct cushioning. A "spaced" 4th pint is impossible — the beer
   only exists as the in-pub drink action.
3. **`press green button` is the escape.** The device is the Sub-Etha
   Thumb; the lights-flicker message is the cue. Confirmed by external
   walkthroughs after three beam deaths.
4. **The save/restore default filename can be poisoned.** Commands
   typed at a death menu (e.g. a stray `south`) become the default
   filename in the next save/restore prompt (`[south.qzl]`), and a bare
   enter then fails. Always type the explicit filename
   `hitchhiker-r59-s851108.qzl`. (Added to AGENTS.md.)
5. **Score so far: 33/400** — analgesic (10), three beers (15),
   peanuts (8). The Vogon ship puzzles (Babel fish, atomic vector
   plotter) are the next big score source.

## Future plans

1. **The Babel fish puzzle (next session).** The dispensing machine in
   the Vogon Hold is the famous multi-step Babel fish sequence (insert
   towel to block the drain, intercept the fish at each obstacle).
   Restore the move-61 checkpoint and work it step by step; the
   walkthroughs already found describe the full chain if a step stalls.
2. **The atomic vector plotter.** The glass case (switch + keyboard)
   needs the correct word typed — per walkthroughs, obtained from the
   glass case recording and the second verse of the Vogon poem (which
   requires the Babel fish first). Expect: listen to recording, endure
   the poetry reading, count guards, type the word, `get plotter`.
3. **The airlock.** After taking the plotter you are thrown into an
   airlock; survive it the same way as on Earth (`press green button`
   on the Thumb, or wait to be blown into space — both work per
   Invisiclues).
4. **Keep banking checkpoints.** Save after every puzzle solved; the
   Babel fish sequence has several irreversible-looking steps (the fish
   can be lost), so save before each risky manipulation.
5. **Seed experiments stay cheap.** The Earth act is now solved
   end-to-end under `-s 42`; if a Vogon-ship gate ever looks
   seed-dependent, restore + vary before restarting from scratch.
6. **Doc debt:** AGENTS.md already carries the new save/update rules
   and the filename-poisoning gotcha; PROGRESS.md (this file) is the
   running record. `.gitignore` still lacks `headless_frotz/*.qzl` —
   add it before committing anything from this directory.

## Session state

- dfrotz process running and idle at the Vogon Hold prompt
  (`process-...422c8c...`); stop it with `QUIT` + enter or
  `tools.process.stop` at session end and verify with
  `tools.process.list`.
- `hitchhiker-r59-s851108.qzl` = Vogon Hold checkpoint (score 33,
  move 61). Untracked; never commit it.

---
*Report generated 2026-09-18 16:16 UTC by Mistral Vibe (Mistral AI).*
