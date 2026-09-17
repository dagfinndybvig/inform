#!/usr/bin/env python3
"""Send a batch of commands to the gym server, one at a time, on one connection."""
import sys
import json
sys.path.insert(0, "autoplay")
from gym_client import GymClient

def main():
    port = 7777
    commands = []
    # Read commands from args or stdin
    if len(sys.argv) > 1:
        cmd_str = " ".join(sys.argv[1:])
        commands = [c.strip() for c in cmd_str.split(";;") if c.strip()]
    else:
        for line in sys.stdin:
            line = line.strip()
            if line and not line.startswith("#"):
                commands.append(line)

    if not commands:
        print("Usage: batch_play.py 'cmd1;;cmd2;;cmd3' or pipe commands via stdin")
        return

    client = GymClient(port=port)
    client.connect()
    client.recv()  # discard resent state on reconnect

    for i, cmd in enumerate(commands):
        resp = client.send(cmd)
        out = resp.get("output", "")
        done = resp.get("done", False)
        preview = out[:600].replace("\n", " | ")
        print(f"[{i+1}] > {cmd}")
        print(f"    {preview}")
        if done:
            print(f"[DONE at command {i+1}]")
            break

    client.close()

if __name__ == "__main__":
    main()
