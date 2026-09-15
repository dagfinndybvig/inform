#!/usr/bin/env python3
"""Live demo: start gym server, play the Lovecraft game turn by turn."""
import os, sys, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gym_client import GymClient, wait_for_server

# Start server
proc = subprocess.Popen(
    [sys.executable, "autoplay/autoplay_server.py",
     "--story", "test_lovecraft.z5", "--port", "7799"],
    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
wait_for_server(proc)

try:
    c = GymClient(port=7799)
    c.connect()

    # Turn 0: opening
    r = c.recv()
    print("=" * 60)
    print("OPENING (done %s)" % r["done"])
    print("=" * 60)
    print(r["output"][:500])
    print("...")

    # Turn 1: examine note
    r = c.send("examine note")
    print("\n" + "=" * 60)
    print(">>> examine note")
    print("done %s" % r["done"])
    print("=" * 60)
    print(r["output"])

    # Turn 2: take key
    r = c.send("examine hearthstone")
    print("=" * 60)
    print(">>> examine hearthstone")
    print("done %s" % r["done"])
    print("=" * 60)
    print(r["output"])

    # Turn 3: go north to garden
    r = c.send("take key")
    print("=" * 60)
    print(">>> take key")
    print("done %s" % r["done"])
    print("=" * 60)
    print(r["output"])

    # Turn 4: examine pond
    r = c.send("n")
    print("=" * 60)
    print(">>> n (go to garden)")
    print("done %s" % r["done"])
    print("=" * 60)
    print(r["output"])

    # Turn 5: look into pond
    r = c.send("look into pond")
    print("=" * 60)
    print(">>> look into pond")
    print("done %s" % r["done"])
    print("=" * 60)
    print(r["output"])

    c.close()
    print("\n[Connection closed. Server still running.]")
finally:
    proc.terminate()
    proc.wait(timeout=5)
    print("[Server shut down.]")
