# Progress Report — Headless Play of The Hitchhiker's Guide to the Galaxy

**Date:** 2026-09-18 15:23 UTC
**Model:** Mistral Vibe (Mistral AI CLI coding agent)
**Setup:** `headless_frotz/dfrotz.exe` (Frotz 2.55 dumb interface, built with
TinyCC), driving `hitchhiker-r59-s851108.z3` as a background process with
incremental output reads. See `README.md` (build) and `AGENTS.md` (recipe).

## What was played

Two full runs with seed `-s 42`, both reaching the same outcome:

- **Moves 1–15 (both runs):** get up; turn on light; take dressing gown;
  wear gown; look in pocket; take analgesic (+10, cures the spinning);
  take screwdriver; take thing; south; south; lie down in front of the
  bulldozer; wait x2; take towel (Ford arrived at move 14, left
  immediately after the towel was taken); save.
- **Run 1:** waits 18–49 (Prosser never swapped despite ~13 waits and
  `prosser, lie down in the mud` / `ask prosser about bulldozer` both
  refused). Vogon ships at move 50; Earth destroyed at move 53.
  Final score: 10 of 400.
- **Run 2:** restored the move-15 save from the death menu (RESTORE +
  default filename — worked exactly), probed Prosser again, waited
  through the same timeline. Died at move 53 again. Score: 10 of 400.

## What was learned

1. **Save/restore is fully functional.** `save` writes
   `hitchhiker-r59-s851108.qzl` in the dfrotz cwd; `RESTORE` from the
   death menu plus a bare enter (default filename) returns the exact
   saved state — score, inventory, position, move counter.
2. **The timeline is deterministic under the seed.** Both runs: Ford
   arrives at move 14, ships at move 50, death at 53. A restore is a
   checkpoint, not a reroll.
3. **The move counter jumps after the bulldozer halts.** Each `wait`
   advances 3 moves while other commands advance 1. Timed events arrive
   sooner (in commands) than the move numbers suggest.
4. **Prosser never swaps.** Roughly 35 waits across two runs, plus
   direct requests and questions, all failed to move him.
5. **The move-15 save is a dead end for survival.** From the standoff
   there are only ~12 commands before the ships, and the countdown
   (50 → 53) allows no escape once the ships arrive.

## Hypotheses for further play

1. **The pub route is the way off the standoff.** In the real game,
   Ford takes Arthur to the pub and the world ends while Arthur is
   safely there (three pints of beer matter later, on the Vogon ship).
   Next experiment: restore to move 15, then go `south` (Country Lane)
   and reach the pub *before* move 50, drinking beer on the way. The
   house is presumably lost, but survival is what matters.
2. **The Prosser swap may be a red herring — or gated on something we
   did not vary.** Candidates: the towel must *not* be taken
   immediately (Ford may need to insist); the swap may require a
   specific phrase (`prosser, wait` / `arthur, ...` style commands);
   or it may simply never be needed because the house is doomed
   anyway. Test by restoring to move 14 (Ford present, towel offered)
   and refusing the towel once.
3. **Seed experiments are cheap.** The hangover gating and possibly the
   Ford/Prosser timing are seed-dependent. If the pub route stalls,
   try `-s 1` and other seeds to see whether event timing shifts.
4. **The +3 move jump changes countdown math.** Any plan that "waits
   until move N" should be re-derived in commands, not moves, or it
   will overshoot gates like the Vogon announcement.
5. **Score ceiling.** 10 of 400 came from the analgesic alone. The
   known big early wins are the pub/beer sequence and the things your
   aunt gave you — the pub route should lift the score well past 10
   even before the Vogon ship puzzles.

## Session state

- Process stopped cleanly; no orphaned dfrotz.
- `hitchhiker-r59-s851108.qzl` (move-15 checkpoint) remains in
  `headless_frotz/` for the next attempt. Untracked; never commit it
  (add `headless_frotz/*.qzl` to `.gitignore` first).

---
*Report generated 2026-09-18 15:23 UTC by Mistral Vibe (Mistral AI).*
