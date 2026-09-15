#!/usr/bin/env python3
"""
autoplay_server.py - Z-machine text-adventure gym server.

Runs a Z-machine v5 story file as a TCP server.  Clients connect, send
one command at a time, and receive the game's response after each
command.  This allows an external agent (e.g. an LLM) to interactively
play an unknown game without pre-scripting commands.

The game state persists between connections: a client may disconnect
and reconnect without losing progress (the opening text is resent).
When a client connects after the game ended, a fresh game starts
automatically.

Protocol: newline-delimited JSON over TCP.

  Request:  {"cmd": "take key"}
  Response: {"output": "Taken.", "done": false, "turn": 1}

Bad requests get {"error": "..."} with "output" empty.

When the game ends (quit, win, or death):
  Response: {"output": "...", "done": true, "turn": 38,
             "score": 90, "deadflag": 2}

  deadflag: 0 = game in progress, 1 = dead, 2 = won

Usage:
    python autoplay/autoplay_server.py --story archive/adventure.z5 --port 7777
                                       [--max-turns N]

Then connect with any TCP client, or use gym_client.py.
"""

import argparse
import json
import os
import queue
import socketserver
import sys
import threading
import traceback

# ztest.py lives in the repo root, one level up.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ztest import ZMachine, Quit


def read_header(story_path):
    """Extract release, serial, and version from a .z5 file."""
    with open(story_path, "rb") as f:
        data = f.read()
    version = data[0]
    release = (data[0x02] << 8) | data[0x03]
    serial = data[0x12:0x18].decode("ascii", errors="replace")
    return version, release, serial


def find_score_globals(story_path):
    """Find which Z-machine global variables hold score, turns, and deadflag.

    Plays a known win path on the Lovecraft game and identifies variables
    that changed to expected values.  Uses a quit-path comparison to
    distinguish deadflag from unrelated globals.  Returns (score_var,
    turns_var, deadflag_var) or (None, None, None).
    """
    try:
        z = ZMachine(story_path, commands=[], seed=1)
    except Exception:
        return None, None, None

    init = {}
    for v in range(16, 256):
        init[v] = z.read_var(v)

    win_cmds = [
        "examine note", "examine hearthstone", "take key", "take notebook",
        "take lantern", "n", "e", "take twig", "w", "s", "d",
        "switch on lantern", "examine crack", "pry coin with twig",
        "take coin", "u", "n", "e", "n", "n", "e", "n", "n",
        "unlock ornate box with rusty key", "open ornate box", "take flower",
        "eat flower", "s", "e", "s", "s", "s", "w", "s", "d",
        "enter clock", "give coin to goddess", "enter clock",
    ]
    try:
        z2 = ZMachine(story_path, commands=win_cmds, seed=1)
        z2.run()
    except Exception:
        pass

    quit_cmds = ["look", "quit", "y"]
    try:
        z3 = ZMachine(story_path, commands=quit_cmds, seed=1)
        z3.run()
    except Exception:
        pass

    # Score: 0 -> 90 after win, still 0 after quit
    # Turns: 1 -> 38 after win
    # Deadflag: 0 -> 2 after win, still 0 after quit
    score_var = None
    turns_var = None
    deadflag_var = None

    for v in range(16, 256):
        win_val = z2.read_var(v)
        quit_val = z3.read_var(v)
        if init[v] == 0 and win_val == 90 and quit_val == 0:
            score_var = v
        if init[v] in (0, 1) and win_val == 38 and quit_val in (0, 1, 2):
            turns_var = v
        if init[v] == 0 and win_val == 2 and quit_val == 0:
            deadflag_var = v

    return score_var, turns_var, deadflag_var


class GameThread(threading.Thread):
    """Runs the Z-machine in a background thread, pausing at each aread.

    Communication with the socket handler uses two queues:
      - cmd_queue:    handler -> game (next command to feed)
      - result_queue: game -> handler (output + done flag after each turn)
    """

    def __init__(self, story_path, seed=None, max_turns=None):
        super().__init__(daemon=True)
        self.story_path = story_path
        self.seed = seed
        self.max_turns = max_turns
        self.turn_count = 0
        self.opening = None    # cached opening text, resent on reconnect
        self.finished = False  # True once the final result has been pushed
        self.cmd_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.z = None

    def run(self):
        self.z = ZMachine(self.story_path, commands=[], seed=self.seed)
        # Monkey-patch next_command to pull from the queue
        self.z.next_command = self._next_command

        try:
            while self.z.running:
                self.z.step()
        except Quit:
            pass
        except Exception:
            # A crashed game thread would otherwise leave the client
            # blocked forever on get_result().  Report and stop.
            output = "".join(self.z.out_buf) if self.z.out_buf else ""
            self.z.out_buf.clear()
            output += "\n[Game thread error]\n%s" % traceback.format_exc()
            self._push_result(output, done=True)
            return

        # Send final output
        output = "".join(self.z.out_buf)
        self.z.out_buf.clear()
        self._push_result(output, done=True)

    def _push_result(self, output, done):
        # The first push of a game is its opening text; cache it so a
        # reconnecting client can be sent it again.
        if self.opening is None:
            self.opening = output
        if done:
            self.finished = True
        self.result_queue.put({"output": output, "done": done})

    def _next_command(self):
        # Flush output to result_queue, then wait for next command
        output = "".join(self.z.out_buf) if self.z.out_buf else ""
        self.z.out_buf.clear()
        self._push_result(output, done=False)

        # Stop after max_turns commands of input (like autoplay.py)
        if self.max_turns is not None and self.turn_count >= self.max_turns:
            self.z.out_buf.append(
                "\n[Turn limit reached after %d turns.]\n" % self.max_turns)
            self.z.running = False
            return None

        # Block until the handler provides the next command
        cmd = self.cmd_queue.get()
        if cmd is None:
            return None
        self.turn_count += 1
        return cmd

    def send_command(self, cmd):
        self.cmd_queue.put(cmd)

    def get_result(self):
        return self.result_queue.get()

    def get_state(self, score_var, turns_var, deadflag_var):
        score = self.z.read_var(score_var) if score_var else 0
        turns = self.z.read_var(turns_var) if turns_var else 0
        deadflag = self.z.read_var(deadflag_var) if deadflag_var else 0
        return score, turns, deadflag


class GymManager:
    """Keeps the current game thread across client connections.

    The game state persists between connections.  When a client connects
    after the previous game ended, a fresh game is started automatically.
    """

    def __init__(self, story_path, seed=None, max_turns=None):
        self.story_path = story_path
        self.seed = seed
        self.max_turns = max_turns
        self.lock = threading.Lock()
        self.game = None

    def current_game(self):
        with self.lock:
            if self.game is None or self.game.finished:
                self.game = GameThread(self.story_path, seed=self.seed,
                                       max_turns=self.max_turns)
                self.game.start()
            return self.game

    def shutdown(self):
        with self.lock:
            if self.game is not None and not self.game.finished:
                self.game.send_command(None)
                self.game.join(timeout=2)


class GymHandler(socketserver.StreamRequestHandler):
    """Handle one client connection to the gym server."""

    def handle(self):
        manager = self.server.manager
        score_var = self.server.score_var
        turns_var = self.server.turns_var
        deadflag_var = self.server.deadflag_var

        game = manager.current_game()

        if game.opening is not None:
            # Reconnecting client: the opening was already consumed by a
            # previous connection, so resend the cached copy.  The game
            # continues from its current state.
            output = game.opening
            done = game.finished
        else:
            # First connection: wait for the opening (game sends it at
            # its first aread).
            result = game.get_result()
            done = result.get("done", False)
            output = result.get("output", "")

        score, turn, deadflag = game.get_state(score_var, turns_var,
                                                 deadflag_var)
        self._send(output, done=done, turn=turn, score=score,
                   deadflag=deadflag)

        while not done:
            try:
                line = self.rfile.readline()
                if not line:
                    break
                req = json.loads(line.decode("utf-8"))
            except (json.JSONDecodeError, ValueError):
                self._send(error="invalid JSON")
                continue

            cmd = req.get("cmd", "")
            if not cmd:
                self._send(error="missing 'cmd' field")
                continue

            # Feed command to game, wait for response
            game.send_command(cmd)
            result = game.get_result()
            done = result.get("done", False)
            output = result.get("output", "")

            score, turn, deadflag = game.get_state(score_var, turns_var,
                                                     deadflag_var)
            self._send(output, done=done, turn=turn, score=score,
                       deadflag=deadflag)

    def _send(self, output="", done=False, turn=0, score=0, deadflag=0,
              error=None):
        resp = {
            "output": output,
            "done": done,
            "turn": turn,
            "score": score,
            "deadflag": deadflag,
        }
        if error is not None:
            resp["error"] = error
        self.wfile.write((json.dumps(resp) + "\n").encode("utf-8"))
        self.wfile.flush()


class GymServer(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_story = os.path.join(here, "adventure_lovecraft.z5")
    ap = argparse.ArgumentParser(
        description="Z-machine text-adventure gym server")
    ap.add_argument("--story", default=default_story,
                    help="path to .z5 story file")
    ap.add_argument("--port", type=int, default=7777,
                    help="TCP port to listen on")
    ap.add_argument("--host", default="127.0.0.1",
                    help="host to bind")
    ap.add_argument("--seed", type=int, default=None,
                    help="seed the PRNG for reproducible random output")
    ap.add_argument("--max-turns", type=int, default=None,
                    help="end the game after this many turns of input")
    args = ap.parse_args()

    version, release, serial = read_header(args.story)
    print("Z-machine gym server", file=sys.stderr)
    print("  Story: %s" % os.path.basename(args.story), file=sys.stderr)
    print("  v%d, Release %d, Serial %s" % (version, release, serial),
          file=sys.stderr)

    # Detect score/turns/deadflag global variables
    print("  Detecting game globals...", file=sys.stderr)
    score_var, turns_var, deadflag_var = find_score_globals(args.story)
    if score_var:
        print("    score: var %d" % score_var, file=sys.stderr)
    if turns_var:
        print("    turns: var %d" % turns_var, file=sys.stderr)
    if deadflag_var:
        print("    deadflag: var %d" % deadflag_var, file=sys.stderr)

    # Game manager: starts the game on the first connection and a fresh
    # game whenever a client connects after the previous one ended.
    manager = GymManager(args.story, seed=args.seed, max_turns=args.max_turns)

    server = GymServer((args.host, args.port), GymHandler)
    server.manager = manager
    server.score_var = score_var
    server.turns_var = turns_var
    server.deadflag_var = deadflag_var

    print("  Listening on %s:%d" % (args.host, args.port), file=sys.stderr)
    print("  Press Ctrl-C to stop.", file=sys.stderr)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down.", file=sys.stderr)
        server.shutdown()
        manager.shutdown()


if __name__ == "__main__":
    main()
