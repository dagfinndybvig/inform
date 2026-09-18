#!/usr/bin/env python3
"""
wfrotz.py - dfrotz-style headless wrapper around WinFrotz.exe (console Frotz
2.32 for Win32), driven through a pseudo-console (pywinpty) with a terminal
emulator (pyte) rendering the 50x100 screen to clean text.

WinFrotz is a GUI-console hybrid that queries the console size and crashes
under a bare pty; the explicit -h/-w switches fix that.  Its output is full
of ANSI cursor-positioning sequences (status-line redraws), so raw capture
is unusable -- pyte maintains the screen and we dump it as plain text.

Usage:
    python wfrotz.py [--story STORY.z5] [--rows 50] [--cols 100] [command ...]

Commands come from positional args, or from stdin (one per line) if none are
given.  Output: the rendered screen after each turn, with the status line
(row 1) and trailing blank lines stripped.
"""

import argparse
import os
import re
import sys
import threading
import time

import pyte
from winpty import PtyProcess

HERE = os.path.dirname(os.path.abspath(__file__))
WINFROTZ = os.path.join(HERE, "WinFrotzConsole", "WinFrotz.exe")


def render(screen):
    lines = [screen.display[y].rstrip() for y in range(screen.lines)]
    # drop leading/trailing blank lines
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Headless WinFrotz wrapper")
    ap.add_argument("--story", required=True)
    ap.add_argument("--rows", type=int, default=50)
    ap.add_argument("--cols", type=int, default=100)
    ap.add_argument("commands", nargs="*")
    args = ap.parse_args()

    commands = list(args.commands)
    if not commands:
        for line in sys.stdin:
            line = line.rstrip("\r\n")
            if line.strip() and not line.startswith("#"):
                commands.append(line)

    screen = pyte.Screen(args.cols, args.rows)
    stream = pyte.ByteStream(screen)

    proc = PtyProcess.spawn(
        "%s -h %d -w %d %s" % (WINFROTZ, args.rows, args.cols, args.story),
        dimensions=(args.rows, args.cols),
        cwd=HERE)

    out = []
    done = threading.Event()

    def reader():
        n = 0
        while not done.is_set() and proc.isalive():
            try:
                c = proc.read(1024)
            except Exception as e:
                sys.stderr.write("[reader: read failed after %d chars: %r]\n"
                                 % (n, e))
                break
            if c:
                n += len(c)
                out.append(c)
                try:
                    stream.feed(c.encode("utf-8", errors="replace"))
                except Exception as e:
                    sys.stderr.write("[reader: feed failed: %r]\n" % e)
                    break
        sys.stderr.write("[reader exited after %d chars, alive=%s]\n"
                         % (n, proc.isalive()))

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    def wait_for_turn(timeout=20):
        """Wait until the screen is stable and shows a fresh '>' prompt.
        Returns False immediately if the interpreter exits (e.g. after quit)."""
        deadline = time.time() + timeout
        last = None
        last_change = time.time()
        while time.time() < deadline:
            if not proc.isalive():
                return False
            cur = render(screen)
            if cur != last:
                last = cur
                last_change = time.time()
            elif cur.rstrip().endswith(">") and time.time() - last_change > 0.5:
                return True
            time.sleep(0.1)
        return False

    for cmd in commands:
        sys.stderr.write("[cmd %r alive=%s]\n" % (cmd, proc.isalive()))
        if not proc.isalive():
            sys.stderr.write("[interpreter exited before %r]\n" % cmd)
            break
        if not wait_for_turn():
            sys.stderr.write("[turn timeout]\n")
        time.sleep(0.2)
        proc.write(cmd + "\r")
        wait_for_turn()
        after = render(screen)
        # incremental: print from the echoed command line to the bottom;
        # scan from the end and match the echo exactly (">e" must not match
        # a stale ">examine note" from an earlier turn)
        marker = ">" + cmd
        rows = after.split("\n")
        start = 0
        for i in range(len(rows) - 1, -1, -1):
            if rows[i].rstrip() == marker:
                start = i
                break
        print("\n".join(r.rstrip() for r in rows[start:]).rstrip())
        print()

    # final screen
    time.sleep(0.5)
    done.set()
    if proc.isalive():
        proc.terminate(force=True)


if __name__ == "__main__":
    main()
