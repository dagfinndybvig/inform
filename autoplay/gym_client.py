#!/usr/bin/env python3
"""
gym_client.py - Client for the Z-machine text-adventure gym server.

Connects to autoplay_server.py, sends commands one at a time, and
prints responses.  Can be used interactively from the terminal or
imported as a library for programmatic play.

Usage (interactive):
    python autoplay/gym_client.py --port 7777

Usage (one command per invocation, for turn-by-turn play from a script):
    python autoplay/gym_client.py --port 7777 --command "look"

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
import threading


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
        # Close the makefile objects too: they hold the underlying
        # connection open, and a socket.close() alone is not enough for
        # the server to see the disconnect.
        for f in (self.rfile, self.wfile):
            if f is not None:
                try:
                    f.close()
                except Exception:
                    pass
        self.rfile = None
        self.wfile = None
        if self.sock:
            self.sock.close()
            self.sock = None


def wait_for_server(proc, timeout=20.0):
    """Block until a gym server subprocess finishes starting.

    Reads proc.stderr (must be a pipe) on a helper thread until the
    server prints its 'Listening on' startup line, so a dead or hung
    server cannot block the caller forever.  Raises RuntimeError on
    timeout or if the server exits before finishing startup.
    """
    outcome = {}

    def read_stderr():
        for line in proc.stderr:
            if b"Listening on" in line:
                outcome["ready"] = True
                return
        outcome["ready"] = False

    t = threading.Thread(target=read_stderr, daemon=True)
    t.start()
    t.join(timeout)
    if "ready" not in outcome:
        raise RuntimeError(
            "gym server did not report ready within %g s" % timeout)
    if not outcome["ready"]:
        raise RuntimeError("gym server exited during startup")


def one_shot(host, port, cmd):
    """Send one command, print the response, and exit.

    The server resends the opening text on every connection; it is
    discarded here so turn-by-turn output stays clean.
    """
    client = GymClient(host=host, port=port)
    client.connect()
    try:
        client.recv()  # opening (resent on reconnect) -- discarded
        resp = client.send(cmd)
        if resp.get("error"):
            print("Server error: %s" % resp["error"], file=sys.stderr)
            return
        sys.stdout.write(resp.get("output", ""))
        if not resp.get("output", "").endswith("\n"):
            sys.stdout.write("\n")
        if resp.get("done"):
            print("\n*** Game ended ***")
    finally:
        client.close()


def main():
    ap = argparse.ArgumentParser(
        description="Client for the Z-machine gym server")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=7777)
    ap.add_argument("--command", default=None, metavar="CMD",
                    help="send one command, print the response, and exit "
                         "(for turn-by-turn play from a script)")
    args = ap.parse_args()

    if args.command is not None:
        one_shot(args.host, args.port, args.command)
        return

    client = GymClient(host=args.host, port=args.port)
    client.connect()
    print("Connected to gym server on %s:%d" % (args.host, args.port),
          file=sys.stderr)

    # Receive opening output
    resp = client.recv()
    if resp.get("error"):
        print("Server error: %s" % resp["error"], file=sys.stderr)
        client.close()
        return
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
        if resp.get("error"):
            print("Server error: %s" % resp["error"], file=sys.stderr)
            continue
        sys.stdout.write(resp.get("output", ""))
        if not resp.get("output", "").endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()

        done = resp.get("done", False)
        if done:
            print("\n*** Game ended ***")

    client.close()


if __name__ == "__main__":
    main()
