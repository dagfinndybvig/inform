# AGENTS.md — Closed_Environment (blind run)

You are about to play a small text game you have never seen. This folder
is a closed environment: everything you need is here, and everything that
could bias you is off limits. Work only from this folder.

## Hard rules (violating any of these ruins the experiment)

- Do NOT read any `.inf` file anywhere in the repository. The game's
  source is the answer key.
- Do NOT read any other `.md`, `.txt`, or `.html` file in this
  repository — no reports, no walkthroughs, no prior transcripts, no
  other AGENTS.md. The only documents you may read are this file and
  the transcript you write yourself.
- Do NOT read the game's git history, diffs, or commit messages to
  learn anything about the game.
- Do NOT search the web for the game, its author, or Inform 6
  walkthroughs.
- Learn the game only from its own output, the way a player would.
- Do NOT commit or push anything. Leave your transcript in this folder.

If you notice you have violated a rule, say so and stop: the run is
contaminated and worthless.

## Setup

`plant.z5` should already be in this folder (it is gitignored). If it is
missing, build it — run this from inside this folder:

    ../../inform6_compiler/inform6.exe +../../inform6lib/inform6lib-master ../industrial_plant.inf plant.z5

Then start the gym server (also from inside this folder):

    python ../gym_ctl.py start --story plant.z5 --port 7789 --max-turns 60

`start` kills any stale gym servers first and blocks until the new one
reports ready. The game ends automatically after 60 turns of input; it
is winnable in far fewer.

## Play

One command per turn, from inside this folder:

    python ../gym_client.py --port 7789 --command "your command here"

Notes:

- One-shot mode discards the game's opening text, so make your first
  command `look`.
- Each invocation is a separate connection; game state lives on the
  server, so you keep your progress between commands.
- `done: true` in the output (shown as `*** Game ended ***`) means the
  game is over. Do not send further commands after that.
- Checkpoint/restore is available and does not consume a turn:
  `--command "__save"` and `--command "__load"`. The game's own
  `save`/`restore` commands do not work; use these instead.

## Transcript

Keep a record as you go. After every turn, append to
`agent_transcript.txt` in this folder: the command you sent and the
game's response. This transcript is the experiment's raw data — do not
edit or summarize it after the fact.

## When the game ends

Stop the server:

    python ../gym_ctl.py stop

Then write a short summary of how you approached the game (strategy,
dead ends, what you learned from the world's feedback) to
`agent_notes.md` in this folder. Leave both files here; the human will
collect them.
