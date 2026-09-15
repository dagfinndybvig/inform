#!/usr/bin/env python3
"""
gym_client.py - Client for the Z-machine text-adventure gym server.

Connects to autoplay_server.py, sends commands one at a time, and
prints responses.  Can be used interactively from the terminal or
imported as a library for programmatic play.

Usage (interactive):
    python autoplay/gym_client.py --port 7777

Usage (library):
    from autoplay.gym_client import GymClient

    client = GymClient(port=7777)
    client.connect()
    opening = client.recv()  # get the opening text
    print(opening["output"])

    resp = client.send("take key")
    print(resp["output"])
    print("done:", resp["done"])

    client.close()
"""

import argparse
import json
import socket
import sys


class GymClient:
    """TCP client for the Z-machine gym server."""

    def __init__(self, host="127.0.0.1", port=7777):
        self.host = host
        self.port = port
        self.sock = None
        self.rfile = None
        self.wfile = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.rfile = self.sock.makefile("rb")
        self.wfile = self.sock.makefile("wb")

    def send(self, cmd):
        """Send a command and return the response dict."""
        req = json.dumps({"cmd": cmd}) + "\n"
        self.wfile.write(req.encode("utf-8"))
        self.wfile.flush()
        return self.recv()

    def recv(self):
        """Receive one response (blocking)."""
        line = self.rfile.readline()
        if not line:
            return {"output": "", "done": True}
        return json.loads(line.decode("utf-8"))

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None


def main():
    ap = argparse.ArgumentParser(
        description="Client for the Z-machine gym server")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=7777)
    args = ap.parse_args()

    client = GymClient(host=args.host, port=args.port)
    client.connect()
    print("Connected to gym server on %s:%d" % (args.host, args.port),
          file=sys.stderr)

    # Receive opening output
    resp = client.recv()
    sys.stdout.write(resp["output"])
    if not resp["output"].endswith("\n"):
        sys.stdout.write("\n")
    sys.stdout.flush()

    done = resp.get("done", False)

    while not done:
        try:
            cmd = input(">")
        except EOFError:
            break
        if not cmd:
            continue

        resp = client.send(cmd)
        sys.stdout.write(resp.get("output", ""))
        if not resp.get("output", "").endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()

        done = resp.get("done", False)
        if done:
            score = resp.get("score", 0)
            deadflag = resp.get("deadflag", 0)
            if deadflag == 2:
                print("\n*** Game won! Score: %d ***" % score)
            elif deadflag == 1:
                print("\n*** Game over (dead) ***")
            else:
                print("\n*** Game ended ***")

    client.close()


if __name__ == "__main__":
    main()
