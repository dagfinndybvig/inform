<img width="1024" height="768" alt="Curses3" src="https://github.com/user-attachments/assets/921e66eb-ffbe-430b-b3a4-d0734b124723" />

# autoplay/ — Play and Serve Z-machine Games

This folder contains tools for playing Z-machine text-adventure games
headlessly — without a human-readable interpreter — and turning an Inform game
into an interactive environment that an AI agent can explore.

## What is the Z-machine?

The Z-machine is a virtual machine designed in 1979 to run Infocom text
adventures. A game is compiled to a `.z5` file (Z-machine version 5),
which contains all the rooms, objects, rules, and text of the game
world. An interpreter loads the file and runs it, reading player commands
and printing descriptions of what the player sees and what happens.

This repo includes its own Z-machine interpreter written from scratch in
Python (`ztest.py` in the repo root), so no external software is needed.

## What is a "world-gym"?

A gym is a controlled environment where an agent — a human, a script, or
an AI like an LLM — can interact with a simulated world one step at a
time. The agent sends a command ("look", "take key", "go north"),
receives the result (room descriptions, object responses, score
changes), decides what to do next, and continues until the game ends.

This is different from pre-scripting a fixed sequence of commands. The
agent can explore freely: it doesn't need to know the game in advance.
It reads the output, reasons about what it sees, and picks the next
action — exactly how a human plays.

Intuitively you might think of it as an "escape room" for LLMs.

## Tools in this folder

### autoplay.py — Interactive terminal player

Plays any `.z5` game in the terminal. Output appears as the game
produces it; you type commands at the `>` prompt. Supports
`--transcript` to record the session to a file with a game-info header,
and `--max-turns N` to stop after a fixed number of input turns.

```bash
python autoplay/autoplay.py --story archive/adventure.z5
```

See [`Z_AUTOPLAY_TOOL.md`](Z_AUTOPLAY_TOOL.md) for full documentation.

### autoplay_server.py — Gym server

Runs a `.z5` game as a TCP server. An external agent connects, sends
one command at a time, and receives the game's response after each
command as structured JSON (output text and a done flag). Supports
`--max-turns N` to end the game after a fixed number of input turns.
Clients may disconnect and reconnect without losing progress; when a
client connects after the game ended, a fresh game starts
automatically.

Use `gym_ctl.py` to manage the server lifecycle:

```bash
python autoplay/gym_ctl.py start --story test_lovecraft.z5 --port 7777
python autoplay/gym_ctl.py status
python autoplay/gym_ctl.py stop
```

See [`Z_AUTOPLAY_GYM.md`](Z_AUTOPLAY_GYM.md) for the protocol, API, and
architecture.

### gym_client.py — Client library and CLI

Connects to the gym server. Can be used interactively from the
terminal, one command per invocation (for turn-by-turn play from a
script), or imported as a Python library for programmatic play.

```bash
# interactive
python autoplay/gym_client.py --port 7777

# one command per invocation; game state persists on the server
python autoplay/gym_client.py --port 7777 --command "look"
```

```python
# library
from gym_client import GymClient

client = GymClient(port=7777)
client.connect()
opening = client.recv()
print(opening["output"])

resp = client.send("take key")
if resp.get("error"):
    print("Server error:", resp["error"])
print(resp["output"])
print("score:", resp["score"])
```

### run_curses_walkthrough.py — Walkthrough smoke test

For a first end-to-end test of the gym, use the Curses walkthrough runner.
It downloads the ignored `autoplay/curses.z5` story file from the canonical
IF Archive link when it is missing, then plays the published walkthrough
through the gym and records a full transcript in
`autoplay/curses_gym_transcript.txt`.

On a clean checkout, run the runner once to fetch the story file, then start
the gym and run it again:

```bash
python autoplay/run_curses_walkthrough.py  # downloads curses.z5; connection may fail
python autoplay/gym_ctl.py start --story autoplay/curses.z5 --port 7777 --max-turns 2200 --seed 1
python autoplay/run_curses_walkthrough.py
```

The first command only needs to be repeated if `autoplay/curses.z5` is
deleted. Stop the server after testing with `python autoplay/gym_ctl.py stop`.

<br>
<img width="896" height="1182" alt="worldmodel" src="https://github.com/user-attachments/assets/c37bd3b1-09cb-4c7c-a12d-ebd94bfaf1e5" />
<br>

## Why model worlds as Z-machine games?

The Z-machine is a general-purpose world simulator. The "adventure"
framing is just one skin. An `.inf` source file can define any set of
interconnected rooms with objects, containers, doors, NPCs, timers, and
state machines. The game compiles to `.z5`, and the gym serves it.

When an LLM is embedded in a world-model like this, its associative
mechanisms are disciplined by the environment's feedback loop: bad
inferences are punished by the game state, good ones are rewarded. The
strict logic lives in the game engine, outside the model — this is
scaffolding around the LLM, not a fix inside it. The model's reasoning
remains associative; the world makes the consequences of each
inference concrete and immediate, which is what helps it deal with
causal chains.

At the same time it is an approach to Explainable AI — with a limit.
An action trail shows what the agent did, never why: LLMs can
rationalize a move after the fact, so the stated reason may not be the
causal one. What the trail gives is behavioral auditability, closer to
an ethogram than to an explanation. That is weaker than reading the
model directly, but it is evidence you can check, replay, and score.

This means you can model a wide range of real-world environments and observe how the LLM behaves:

- **An industrial plant** — rooms are zones, objects are valves and
  gauges, the player is an operator doing a safety walkthrough. Score
  for completing the procedure in the right order.
- **A building evacuation** — rooms are floors and hallways, doors lock
  and unlock, fire spreads via timers, the player must find exits and
  guide people out.
- **A guided tour or onboarding** — rooms are stations, objects are
  equipment, examining things teaches the player how they work.

The agent doesn't need to know the world in advance. It connects to the
gym, reads the opening description, explores, examines objects, opens
doors, and builds a mental model of the world — turn by turn, exactly
like a person arriving somewhere new. You score the agent on whether it
completed the objective: did it finish the safety checklist, evacuate
everyone, find and fix the problem?

Two caveats bound what such experiments can show. First, the
micro-world problem (Dreyfus's critique of GOFAI): these worlds are
closed, deterministic, and engineered to be solvable, so competence
inside them may not transfer to open-world situations. Second,
training-data contamination: Infocom-style games are well represented
in LLM training data, so winning may measure familiarity with
adventure-game conventions rather than world-modeling. Both argue for
treating the gym as one instrument among several, not as a verdict.

The good news? All the infrastructure already exists. Writing a new `.inf` file is the only
creative work needed to create a new world. 

And even that can be done by an agent, as the top-level project of this repo shows.

## How this compares to Go and reinforcement learning

Intellectually the setup descends from GOFAI's micro-worlds —
SHRDLU's blocks world and Newell and Simon's physical symbol system
hypothesis — and from the modern neuro-symbolic and agent-benchmark
lines (TextWorld, ALFWorld, ReAct). A compiled `.z5` file is a fully
specified possible world: every object, rule, and causal chain
explicit. Judging an agent inside one by its actions rather than its
self-reports tests practical reasoning under feedback, which static
benchmarks cannot.

The gym borrows RL's vocabulary (agent, environment, step, reward) but
inverts the economics. In Go, the environment is nearly free and the
agent is expensive to train; here the environment is cheap but each
step costs an LLM inference, so the millions of episodes from-scratch
RL needs are out of reach, and credit assignment across a long text
episode is much weaker than a board position's win probability. The
nearer relatives are text-game RL benchmarks like Jericho, TextWorld,
and ALFWorld. This setup is an evaluation and data-collection harness,
not a training loop: the realistic RL-adjacent use is recording
winning transcripts for offline fine-tuning, not online RL against
the simulator.

## A first step: the industrial plant MVP

Both caveats above have a concrete response in this folder:
`industrial_plant.inf` ("The Morning Shift"), a minimal manufacturing
line rather than an adventure game. The agent runs one door unit
through a five-step process — press, cure, assemble, inspect, ship —
across six stations, and the shipping dock refuses any unit without a
QC pass, so the process order must be learned from environmental text
(the process sheet, machine stencils, refusal messages), not from
adventure-game conventions.

This is the contamination-controlled half of the experiment. Neither
world is in training data — the Lovecraft game was written for this
project — but contamination operates at the level of genre
conventions, not specific worlds: the Lovecraft game is idiomatic
adventure-game Inform (take key, unlock box, give coin to the NPC), so
fifty years of adventure-game text transfers. The plant's conventions
are industrial-process conventions instead, which are thin in training
data. The Lovecraft game serves as the positive control — same engine,
familiar conventions — and the delta between the two runs is the
finding. The micro-world caveat still stands: the
plant is closed, deterministic, and engineered to be solvable. But the
protocol is now runnable end to end: serve the `.z5` through the gym,
record the transcript blind, and score whether the agent discovered
the process, where its adventure-game priors misled it, and whether
the action trail shows genuine process learning.

The first empirical material now exists. `Report_Industrial_Plant.md`
documents the world and reproduces a first agent run through the gym:
10/10 in 18 turns, with two process errors — a verb chosen from the
room's surface form, and a premature ship attempt that the QC gate
refused — both caught and corrected by the world's feedback alone.
The deterministic reference playthrough
(`industrial_plant_transcript.txt`, 10/10 in 16 turns) and the
annotated agent transcript (`industrial_plant_agent_transcript.txt`)
are in this folder. One disclosure bounds the run: the agent and the
world's author are the same system, so it demonstrates the protocol,
not the finding. The finding awaits a blind agent — same procedure,
then compare against this run and the Lovecraft positive control.

## Closed environment: blind agent trial

`Closed_Environment/` is a self-contained subfolder set up for blind
agent runs. It contains a `.z5` game file (gitignored), its own
`AGENTS.md` with hard rules that wall off the answer key (no reading
`.inf` source, no other docs or transcripts, no git history, no web
searches), and instructions for starting the gym server on port 7789
and playing one command at a time. The agent keeps a turn-by-turn
transcript and writes a summary; these are the experiment's raw data.

A trial run has been performed. An agent (model `glm-5-2`) played
`plant.z5` blind through the gym, won with 10/10 in 13 turns, and
left a transcript (`agent_transcript.txt`), notes
(`agent_notes.md`), and a full write-up (`TODO.md`) in the folder.
The run confirmed the closed-environment harness works end to end.
The game's in-world process sheet made the run straightforward; the
write-up recommends harder games to exercise discovery rather than
execution, and notes a protocol tightening for append-only
transcript writes.
