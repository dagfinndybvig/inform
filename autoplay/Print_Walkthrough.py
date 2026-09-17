#!/usr/bin/env python3
"""Pretty-print a Curses gym transcript."""

import argparse
import os
import re
import sys


DEFAULT_TRANSCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "curses_gym_transcript.txt",
)
TURN_HEADER = re.compile(r"^\[0*(\d+)\] > (.*)$")


def clean_line(line):
    """Remove terminal-style spacing while retaining response indentation."""
    if not line.strip():
        return ""
    stripped = line.strip()
    if "Score:" in stripped or "Turns:" in stripped:
        return re.sub(r"\s+", " ", stripped)
    return line.rstrip()


def prettyprint(source):
    lines = source.splitlines()
    output = []
    turn = None
    response = []
    started = False

    def write_turn():
        if turn is None:
            return
        output.append("=" * 72)
        output.append("Turn %s: %s" % turn)
        output.append("-" * 72)
        cleaned = [clean_line(line) for line in response]
        while cleaned and not cleaned[0]:
            cleaned.pop(0)
        while cleaned and not cleaned[-1]:
            cleaned.pop()
        output.extend(cleaned)

    for line in lines:
        match = TURN_HEADER.match(line)
        if match:
            write_turn()
            turn = match.groups()
            response = []
            started = True
        elif line == "[GAME ENDED]":
            write_turn()
            turn = None
            response = []
            output.extend(("=" * 72, "GAME ENDED"))
        elif turn is None and started:
            output.append(line.rstrip())
        else:
            response.append(line)

    write_turn()
    return "\n".join(output).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Pretty-print the Curses gym transcript")
    parser.add_argument("transcript", nargs="?", default=DEFAULT_TRANSCRIPT,
                        help="transcript to format (default: %(default)s)")
    parser.add_argument("-o", "--output", metavar="FILE",
                        help="write formatted output to FILE instead of stdout")
    args = parser.parse_args()

    with open(args.transcript, encoding="utf-8") as source:
        formatted = prettyprint(source.read())
    if args.output:
        with open(args.output, "w", encoding="utf-8") as destination:
            destination.write(formatted)
    else:
        sys.stdout.write(formatted)


if __name__ == "__main__":
    main()