# Report: The Industrial Plant MVP and a First Agent Run

Date: 2026-09-18
World: `autoplay/industrial_plant.inf` ("The Morning Shift")
Agent: Mistral Vibe (GLM), via the gym server (`autoplay_server.py`)
Result: **WIN — 10/10 in 18 turns**, two process errors, both caught
by the world and corrected from its feedback.

## Why this world exists

The README's closing notes raise two caveats that bound what gym
experiments can show: the micro-world problem (Dreyfus) and
training-data contamination. `industrial_plant.inf` is the concrete
response to the second: a minimal manufacturing line rather than an
adventure game, so the conventions an agent must operate under are
industrial-process conventions (stations, process order, QC gates)
instead of fifty years of adventure-game text.

Neither world is in training data — the Lovecraft game was written
for this project — but contamination operates at the level of genre
conventions, not specific worlds. The Lovecraft game is idiomatic
adventure-game Inform (take key, unlock box, give coin to the NPC);
the plant is not. The Lovecraft game therefore serves as the positive
control — same engine, familiar conventions — and the delta between
the two runs is the finding.

## The world

A linear production line of six stations:

    Loading Bay -> Press Shop -> Curing Oven -> Assembly Line
                -> Quality Control -> Shipping Dock

The agent must run one door unit through a five-step process: take
blank, press, cure, attach bracket, inspect, ship. The shipping dock
refuses any unit without a QC pass, so the process order must be
learned from environmental text — the process sheet, machine stencils,
and refusal messages. Everything needed to solve the world is in-game;
there is no adventure-game vocabulary to lean on.

A deterministic reference playthrough exists
(`autoplay/industrial_plant_transcript.txt`): 10/10 in 16 turns,
including the QC-gate refusal and recovery. It establishes that the
world is solvable from its own text.

## The experimental run

The agent connected to the gym server and played one command at a
time, decisions made from game output only. The full trail
(`autoplay/industrial_plant_agent_transcript.txt`), reproduced here:

    > look
    Loading Bay — steel shelving, a clipboard on the wall, a pallet of
    raw steel blanks. You can see a steel blank here.

    > examine clipboard
    PROCESS SHEET -- RUN 47, ONE DOOR UNIT.
    1. Take a steel blank.
    2. PRESS SHOP: press the blank (type 'press blank').
    3. CURING OVEN: cure the pressed panel (type 'cure panel').
    4. ASSEMBLY LINE: attach the panel to a bracket at the workbench.
    5. QUALITY CONTROL: inspect the finished unit.
    6. SHIPPING DOCK: ship the unit. No QC pass, no shipment.

    > take blank          -> Taken.
    > e                   -> Press Shop
    > press blank         -> pressed door panel, still warm at the edges
    > e                   -> Curing Oven

    > put panel in oven
    The curing oven can't contain things.
    [ERROR 1: physical phrasing from the room name; the sheet's verb
    was 'cure panel'. Corrected from the world's refusal.]

    > cure panel          -> cured, ready for the bench
    > e                   -> Assembly Line (steel bracket visible)
    > take bracket        -> Taken.
    > attach panel to bracket -> finished door unit
    > e                   -> Quality Control
    > e                   -> Shipping Dock

    > ship unit
    The manifest clipboard refuses you: no QC pass number, no
    shipment. Inspect the unit first.
    [ERROR 2: premature ship attempt despite the sheet's order;
    caught by the QC gate. Recovered by backtracking.]

    > w                   -> Quality Control
    > inspect unit        -> PASS lamp comes on, QC number stamped
    > e                   -> Shipping Dock
    > ship unit           -> Run 47 is complete.

    *** You have won ***
    In that game you scored 10 out of a possible 10, in 18 turns.

## What the trail shows

Two errors, both informative:

1. **Verb selection from surface form.** At the curing oven the agent
   tried `put panel in oven` — the physical phrasing suggested by the
   room name — before the sheet's verb `cure panel`. The world refused
   ("The curing oven can't contain things") and the correction came
   from that refusal, not from re-reading the sheet. The environment's
   feedback loop did the disciplining.

2. **Goal pull overriding written instructions.** Despite the sheet's
   explicit order (inspect, then ship), the agent went to the dock and
   tried to ship first. The QC gate refused it and the agent
   backtracked. This is the central phenomenon: the scaffolding — a
   rule in the game engine, outside the model — caught an inference
   the agent's own reading did not.

Both errors were recovered from in one turn each, using only the
world's refusal messages. The action trail is behavioral auditability
in the README's sense: it shows what the agent did and where its
priors pulled, without claiming to show why.

## Limitations

The disclosure that limits this run: the agent and the world's author
are the same system. The world was written earlier the same day, so
the agent knew the QC gate existed and knew the verb set. The errors
were organic to how the run was played, but the run is not
contamination-controlled — it demonstrates the protocol, not the
finding.

The actual finding requires an LLM that never saw the `.inf`: same
procedure (serve the world, play blind, record everything, annotate
errors), then compare that transcript against this one and against the
Lovecraft positive control. The micro-world caveat also still stands:
the plant is closed, deterministic, and engineered to be solvable, so
competence inside it does not transfer to open-world situations.

## Artifacts

- `autoplay/industrial_plant.inf` — the world (source)
- `autoplay/industrial_plant.z5` — local build (gitignored)
- `autoplay/industrial_plant_transcript.txt` — deterministic reference
  playthrough, 10/10 in 16 turns
- `autoplay/industrial_plant_agent_transcript.txt` — the agent run
  reproduced above
