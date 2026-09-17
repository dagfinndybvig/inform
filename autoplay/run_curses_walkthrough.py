#!/usr/bin/env python3
"""Run the published Curses walkthrough through the gym and record a transcript."""

import html
import os
import re
import sys
import tempfile
import urllib.request

sys.path.insert(0, ".")
from gym_client import GymClient


WALKTHROUGH_URL = "https://plover.net/~davidw/sol/c/curse93.html"
STORY_URL = "https://ifarchive.org/if-archive/games/zcode/curses.z5"
STORY_PATH = "autoplay/curses.z5"
TRANSCRIPT = "autoplay/curses_gym_transcript.txt"


def ensure_story_file():
    if os.path.isfile(STORY_PATH) and os.path.getsize(STORY_PATH) > 0:
        return
    directory = os.path.dirname(STORY_PATH)
    fd, temporary_path = tempfile.mkstemp(dir=directory, suffix=".download")
    os.close(fd)
    try:
        urllib.request.urlretrieve(STORY_URL, temporary_path)
        if os.path.getsize(temporary_path) == 0:
            raise RuntimeError("downloaded story file is empty")
        os.replace(temporary_path, STORY_PATH)
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)


def walkthrough_commands():
    page = urllib.request.urlopen(WALKTHROUGH_URL, timeout=30).read().decode()
    blocks = re.findall(r"<kbd>(.*?)</kbd>", page, re.S)
    start = next(i for i, block in enumerate(blocks)
                 if "verbose. i. x biscuit." in block)
    commands = []
    for block in blocks[start:]:
        text = html.unescape(re.sub(r"<[^>]+>", " ", block))
        text = re.sub(r"\s+", " ", text).strip()
        if text == "save":
            break
        text = re.sub(r"^>\s*", "", text)
        for command in re.split(r"\.\s+", text):
            command = command.strip(" .")
            if not command or command.lower() in {
                "say odd -- or -- say even", "say odd or say even",
            }:
                continue
            if command.startswith("SAY LAGACH TO ARTWORK"):
                continue
            commands.append(command)
    return commands


def main():
    ensure_story_file()
    client = GymClient(port=7777)
    client.connect()
    try:
        opening = client.recv()
        with open(TRANSCRIPT, "w", encoding="utf-8") as log:
            log.write("Transcript of Curses played through the gym server\n")
            log.write("Walkthrough: %s\n\n" % WALKTHROUGH_URL)
            log.write("[OPENING]\n%s\n" % opening.get("output", ""))
            commands = walkthrough_commands()
            for number, command in enumerate(commands, 1):
                response = client.send(command)
                output = response.get("output", "")
                log.write("\n[%04d] > %s\n%s\n" % (number, command, output))
                log.flush()
                if response.get("done"):
                    log.write("\n[GAME ENDED]\n")
                    break
            else:
                log.write("\n[COMMAND STREAM EXHAUSTED]\n")
        print("commands:", number)
        print("done:", response.get("done"))
        print("transcript:", TRANSCRIPT)
        print("win:", "*** You have won ***" in output)
        print(output[-500:])
    finally:
        client.close()


if __name__ == "__main__":
    main()