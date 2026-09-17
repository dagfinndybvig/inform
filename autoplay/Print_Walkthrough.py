#!/usr/bin/env python3
"""Pretty-print a Curses gym transcript."""

import argparse
import html
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
    if stripped.startswith(">"):
        return ""
    if " -- " in stripped:
        return ""
    if "Score:" in stripped or "Turns:" in stripped:
        return re.sub(r"\s+", " ", stripped)
    return line.rstrip()


def prettyprint(source):
    lines = source.splitlines()
    turns = []
    turn = None
    response = []
    started = False
    game_ended = False

    def write_turn():
        if turn is None:
            return
        cleaned = [clean_line(line) for line in response]
        while cleaned and not cleaned[0]:
            cleaned.pop(0)
        while cleaned and not cleaned[-1]:
            cleaned.pop()
        turns.append((turn, cleaned))

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
            game_ended = True
        elif turn is not None:
            response.append(line)

    write_turn()
    articles = []
    for (number, command), response_lines in turns:
        response_text = "\n".join(response_lines)
        articles.append(
            "<article class=\"turn\">\n"
            "  <h2>Turn %s <code>&gt; %s</code></h2>\n"
            "  <pre>%s</pre>\n"
            "</article>" % (
                html.escape(number),
                html.escape(command),
                html.escape(response_text),
            )
        )
    ended = "<p class=\"ended\">GAME ENDED</p>" if game_ended else ""
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Curses Walkthrough Transcript</title>
  <style>
    :root { color-scheme: light; font-family: system-ui, sans-serif; }
    body { margin: 0 auto; max-width: 64rem; padding: 2rem 1rem; color: #202124; background: #f7f7f5; }
    h1 { margin-top: 0; font-size: 1.8rem; }
    .turn { margin: 1rem 0; padding: 1rem; background: white; border: 1px solid #d8d8d2; border-radius: 6px; }
    h2 { margin: 0 0 .75rem; font-size: 1rem; color: #43566b; }
    code { font-weight: normal; color: #222; }
    pre { margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; font: .92rem/1.45 ui-monospace, SFMono-Regular, Consolas, monospace; }
    .ended { padding: 1rem; font-weight: 700; color: #176b3a; border: 1px solid #8ac6a4; background: #eaf7ee; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>Curses Walkthrough Transcript</h1>
%s
  %s
</body>
</html>
""" % ("\n".join(articles), ended)


def main():
    parser = argparse.ArgumentParser(
        description="Render the Curses gym transcript as HTML")
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