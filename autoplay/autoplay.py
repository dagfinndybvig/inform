#!/usr/bin/env python3
"""
autoplay.py - Interactive headless Z-machine v5 interpreter.

Plays any .z5 story file interactively in the terminal.  Output is
printed as the game produces it; input is read line-by-line from stdin
at each prompt.  No scripting, no pre-fed command list.

Usage:
    python autoplay/autoplay.py [--story STORY.z5] [--seed N]

Default story is adventure_lovecraft.z5 in the repo root.
"""

import argparse
import os
import sys

# ztest.py lives in the repo root, one level up.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ztest import ZMachine, Quit


class InteractiveZMachine(ZMachine):
    """ZMachine that reads commands interactively from stdin."""

    def next_command(self):
        # Flush any accumulated output before prompting.
        if self.out_buf:
            text = "".join(self.out_buf)
            sys.stdout.write(text)
            if not text.endswith("\n"):
                sys.stdout.write("\n")
            sys.stdout.flush()
            self.out_buf.clear()
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
    args = ap.parse_args()

    z = InteractiveZMachine(args.story, commands=[], seed=args.seed)
    try:
        z.run()
    except Quit:
        pass

    # Flush any remaining output after the game ends.
    if z.out_buf:
        sys.stdout.write("".join(z.out_buf))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
