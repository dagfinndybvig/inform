#!/usr/bin/env python3
"""End-to-end test for the gym server + client."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gym_client import GymClient, wait_for_server

def test_game(story_path, commands, expect_win=True):
    # Start server
    proc = subprocess.Popen(
        [sys.executable, "autoplay/autoplay_server.py",
         "--story", story_path, "--port", "7788"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Wait for server to be ready
    wait_for_server(proc)

    try:
        client = GymClient(port=7788)
        client.connect()

        # Receive opening
        resp = client.recv()
        print("=== Opening ===")
        print(resp["output"][:200])
        print("done:", resp.get("done"))
        print()

        # Collect all output to check for win text
        all_output = resp.get("output", "")

        # Send commands
        for cmd in commands:
            resp = client.send(cmd)
            print(">>> %s" % cmd)
            print(resp["output"][:200])
            print("done:", resp.get("done"))
            print()
            all_output += resp.get("output", "")
            if resp.get("done"):
                break

        if expect_win:
            assert "*** You have won ***" in all_output, \
                "Expected win text in output"
            assert "90 out of a possible 90" in all_output, \
                "Expected score 90 in output"
            print("WIN: output contains 'You have won' and score 90/90")

        client.close()
    finally:
        proc.terminate()
        proc.wait(timeout=5)

print("=" * 60)
print("TEST 1: archive/adventure.z5 (short game)")
print("=" * 60)
test_game("archive/adventure.z5", ["take key", "take lantern", "north", "look", "quit", "y"],
          expect_win=False)

print()
print("=" * 60)
print("TEST 2: test_lovecraft.z5 (full win path)")
print("=" * 60)
test_game("test_lovecraft.z5", [
    "examine note", "examine hearthstone", "take key", "take notebook",
    "take lantern", "n", "e", "take twig", "w", "s", "d",
    "switch on lantern", "examine crack", "pry coin with twig",
    "take coin", "u", "n", "e", "n", "n", "e", "n", "n",
    "unlock ornate box with rusty key", "open ornate box", "take flower",
    "eat flower", "s", "e", "s", "s", "s", "w", "s", "d",
    "enter clock", "give coin to goddess", "enter clock",
], expect_win=True)

print("\nAll tests passed.")
