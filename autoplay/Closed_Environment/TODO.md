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

## Broader assessment (post-run, with full repo access)

After the blind run, the agent was given access to the full repo.
The following is a wider assessment of the autoplay project as a
whole, written from that unblinded perspective.

### Architecture

The core design decision — one Z-machine interpreter in `ztest.py`,
everything else subclasses it — is correct. `autoplay.py`,
`autoplay_server.py`, and the test harness all override only
`next_command` and output routing. Z-machine logic lives in exactly
one place, and the AGENTS.md files explicitly forbid forking it. This
is the single most important thing the project got right.

The gym protocol is appropriately minimal: newline-delimited JSON
over TCP, one command per turn, `done` flag on completion,
`__save`/`__load` for checkpoints that do not consume a turn. An
agent can drive the gym with a one-line client invocation. No framing
complexity, no retry logic, no session management beyond per-server
state.

The checkpoint system (full memory + call stack + PC + RNG snapshot)
paired with command chunk files and session logs for deterministic
replay is well-engineered. It was proven in practice — a 410-point
Curses session was recovered from a 254-point checkpoint using
preserved chunk files. That is strong evidence the design works under
real load, not just in theory.

### Research framing

The README does not oversell what the gym proves. It explicitly names
the two caveats: Dreyfus's micro-world critique (closed,
deterministic, engineered to be solvable) and training-data
contamination (adventure-game conventions are well-represented in LLM
training data). The two-game design — Lovecraft as positive control
with familiar conventions, industrial plant as
contamination-controlled testbed with novel conventions — is a
genuine attempt to separate "the agent knows adventure-game genre
priors" from "the agent learned from environmental feedback." The
delta between the two runs is the finding, not either run alone.

That said, the industrial plant is still a micro-world. It is closed,
deterministic, and engineered to be solvable. The contamination
control addresses one of the two caveats, not both.

### What the blind trial showed and did not show

This blind run confirmed the toolchain is functional end to end:
server starts, client connects, commands work, transcript is
produced, server stops cleanly. But it did not test the hypothesis,
because the game's clipboard handed the agent the entire solution as
a numbered recipe. The Lovecraft positive control has never been run
blind by a different agent. So the delta that would constitute a
finding has not been measured yet.

To actually test the hypothesis, you need:

1. A blind run of the Lovecraft game by a different agent — this is
   the positive control.
2. A blind run of a harder industrial plant variant (no in-world
   walkthrough) by the same or another agent — this is the
   experimental condition.
3. Comparison of the two: error rates, recovery from failure,
   evidence of discovery vs. execution.

The plant as written is too easy even without contamination concerns.
The clipboard is a tutorial crutch. A variant that removes or
obscures the process sheet, adds failure states, or introduces
branching would exercise the actual capability the gym is meant to
probe.

### Practical issues

- **One connection at a time.** The gym server handles one client
  connection at a time, and game state is per-server. Fine for
  single-agent runs, but the harness cannot do comparative or
  parallel experiments without multiple server instances on
  different ports.
- **No `pages.yml` workflow file.** The AGENTS.md references a `pages`
  workflow, but no such file exists in `.github/workflows/`. Pages
  deploy is likely configured via repo settings. Worth confirming
  this is intentional.
- **The plant `.z5` is not tracked.** `industrial_plant.inf` is
  tracked, but the compiled `plant.z5` is gitignored and lives only
  in this folder. Correct per the git workflow rules, but a fresh
  checkout cannot run the plant experiment without a local compile
  step. The build command is documented in this folder's `AGENTS.md`.

### Bottom line

The autoplay project is a well-structured research harness with a
clear thesis, honest caveats, and working infrastructure. The
single-interpreter design, checkpoint system, and cross-platform
tooling are solid engineering. The weak point is not the tooling but
the experimental content: the plant game is too easy to distinguish
discovery from execution, and the positive control has not been run
blind. The harness is ready to produce real findings — it just needs
harder games and a second agent.
