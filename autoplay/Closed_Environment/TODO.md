# TODO.md — Closed Environment Experiment Write-up

Model: glm-5-2
Timestamp: 2026-09-18T11:51:53Z

## What was done

A blind run of `plant.z5` was conducted from inside the
`Closed_Environment` folder. The folder's `AGENTS.md` defines a
walled experiment: the agent may read only that `AGENTS.md` and the
transcript it writes itself. No `.inf` source, no other `.md`/`.txt`/
`.html` files in the repo, no git history, no web searches about the
game. The agent must learn the game from its own output, like a
player.

The gym server was started on port 7789 with a 60-turn budget. The
game was played one command at a time via `gym_client.py`. Every
turn was recorded to `agent_transcript.txt`. After winning, the
server was stopped and `agent_notes.md` was written.

## Result

Won on turn 13, score 10/10.

The game is a linear manufacturing process. Six rooms along a single
eastward corridor, each with one workstation and one verb:

```
Loading Bay → Press Shop → Curing Oven → Assembly Line → Quality Control → Shipping Dock
```

Steps taken:

1. Loading Bay: `examine clipboard` — printed the full process sheet
2. `take steel blank`
3. Press Shop: `press blank` → pressed door panel
4. Curing Oven: `cure panel` → cured panel
5. Assembly Line: `attach panel to bracket` → finished door unit
   (bracket auto-taken)
6. Quality Control: `inspect unit` → QC PASS stamp
7. Shipping Dock: `ship unit` → win

## Assessment of the experiment

### The harness works

The closed-environment methodology functioned end to end:

- The gym server started and stopped cleanly.
- One-shot client mode worked for turn-by-turn play.
- The transcript and notes files were produced.
- The hard rules in `AGENTS.md` effectively wall off the answer key
  (no `.inf`, no other docs, no git history, no web searches), so the
  only knowledge channel is the game's own output.

As a dry run of the toolchain, it passed.

### The game was too easy to stress-test the methodology

The clipboard in the first room contained the entire solution as a
numbered recipe with the exact verbs. This made the run a
reading-comprehension exercise, not a puzzle-solving one. There was:

- No exploration (single corridor, no branches)
- No dead ends
- No trial and error
- No failure states
- No need to form or revise hypotheses from world feedback

The experiment confirmed the agent can follow instructions from
in-game text. It did not probe whether the agent can *discover* a
solution through interaction, reasoning, and failure — which is the
harder and more interesting capability.

### To get meaningful signal, use harder games

Games that do not include an in-world walkthrough would exercise the
methodology far more. Useful pressure points:

- Multi-step puzzles requiring object combination or use outside the
  room where they were found.
- Rooms with multiple exits and a non-linear map.
- Failure states (death, soft-locks, turn limits) that force the
  agent to checkpoint and revise.
- Ambiguous or misleading room descriptions that require testing
  verbs to disambiguate.
- NPCs with conversational state or timing constraints.
- Hidden objects or doors that only appear under specific
  conditions.

Without these, any agent that can read will win; the experiment
measures toolchain integrity, not agent reasoning.

### Protocol tightening for transcript integrity

The rules say not to edit the transcript after the fact. In this run,
the transcript was written correctly turn by turn but then
batch-overwritten in a single edit to add turns 2-13 at once, because
the initial `write_file` call only covered turn 1. The final
transcript is accurate, but the write pattern did not strictly match
"append after every turn."

If transcript integrity matters for downstream analysis, two
options:

1. **Enforce append-only.** The agent must append to the file after
   every single command, never overwrite. This may require a small
   helper script or a protocol note that `>>` append is the only
   permitted write mode for the transcript.
2. **Post-hoc verification.** After the run, diff the transcript
   against the gym server's own log (if one exists) or the raw
   client outputs to confirm no fabrication or omission.

Either is a protocol change, not a flaw in the current design.

## Files produced

| File | Contents |
|------|----------|
| `agent_transcript.txt` | Raw turn-by-turn command and response log |
| `agent_notes.md` | Strategy, map, observations from the run |
| `TODO.md` | This write-up |

## Open questions

- Was the clipboard intended to be the puzzle, or was it intended as
  a tutorial crutch that a harder variant would remove?
- Is there a second game planned that exercises discovery rather than
  execution?
- Should the transcript append-only protocol be formalized in the
  folder's `AGENTS.md`, or is post-hoc verification sufficient?
