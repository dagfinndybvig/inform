#!/usr/bin/env python3
"""
autoplay.py - Interactive headless Z-machine v5 interpreter.

Plays any .z5 story file interactively in the terminal.  Output is
printed as the game produces it; input is read line-by-line from stdin
at each prompt.  No scripting, no pre-fed command list.

Usage:
    python autoplay/autoplay.py [--story STORY.z5] [--seed N]
                                [--transcript FILE] [--max-turns N]

Default story is adventure_lovecraft.z5 in the repo root.
"""

import argparse
import datetime
import os
import sys

# ztest.py lives in the repo root, one level up.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ztest import ZMachine, Quit


def read_header(story_path):
    """Extract release number, serial, and Z-machine version from a .z5 file."""
    with open(story_path, "rb") as f:
        data = f.read()
    version = data[0]
    release = (data[0x02] << 8) | data[0x03]
    serial = data[0x12:0x18].decode("ascii", errors="replace")
    return version, release, serial


class InteractiveZMachine(ZMachine):
    """ZMachine that reads commands interactively from stdin."""

    def __init__(self, *args, transcript=None, story_path=None, max_turns=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.transcript = transcript
        self.story_path = story_path
        self.max_turns = max_turns
        self.turn_count = 0

    def _write(self, text):
        """Write text to stdout and optionally the transcript."""
        sys.stdout.write(text)
        if self.transcript is not None:
            self.transcript.write(text)

    def _flush_output(self):
        """Flush accumulated game output to stdout and transcript."""
        if self.out_buf:
            text = "".join(self.out_buf)
            self._write(text)
            if not text.endswith("\n"):
                self._write("\n")
            sys.stdout.flush()
            self.out_buf.clear()

    def next_command(self):
        self._flush_output()
        self.turn_count += 1
        if self.max_turns is not None and self.turn_count > self.max_turns:
            self._write("\n[Turn limit reached after %d turns.]\n"
                        % self.max_turns)
            self.running = False
            return None
        try:
            return input(">")
        except EOFError:
            self.running = False
            return None


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_story = os.path.join(here, "adventure_lovecraft.z5")
    ap = argparse.ArgumentParser(
        description="Interactive headless Z-machine v5 interpreter")
    ap.add_argument("--story", default=default_story,
                    help="path to .z5 story file")
    ap.add_argument("--seed", type=int, default=None,
                    help="seed the PRNG for reproducible random output")
    ap.add_argument("--transcript", default=None,
                    help="write game output to this file")
    ap.add_argument("--max-turns", type=int, default=None,
                    help="stop after this many turns of input")
    args = ap.parse_args()

    version, release, serial = read_header(args.story)

    transcript = None
    if args.transcript:
        transcript = open(args.transcript, "w", encoding="utf-8")
        transcript.write("Transcript of %s\n" % os.path.basename(args.story))
        transcript.write("Z-machine v%d, Release %d, Serial %s\n"
                         % (version, release, serial))
        transcript.write("Recorded: %s\n" % datetime.datetime.now()
                         .strftime("%Y-%m-%d %H:%M:%S"))
        if args.seed is not None:
            transcript.write("Seed: %d\n" % args.seed)
        transcript.write("=" * 40 + "\n\n")

    z = InteractiveZMachine(args.story, commands=[], seed=args.seed,
                           transcript=transcript, story_path=args.story,
                           max_turns=args.max_turns)
    try:
        z.run()
    except Quit:
        pass

    z._flush_output()

    if transcript is not None:
        transcript.close()


if __name__ == "__main__":
    main()
