#!/usr/bin/env python3
"""
gym_ctl.py - Start, stop, and check the Z-machine gym server.

Usage:
    python autoplay/gym_ctl.py start [--story PATH] [--port N] [--max-turns N] [--seed N]
    python autoplay/gym_ctl.py stop
    python autoplay/gym_ctl.py status

start:  Kills any existing gym server, launches a fresh one in the
        background, and waits until it reports "Listening on".  The
        PID is saved to a file so stop can kill exactly the right
        process.

stop:   Kills the running gym server (if any) and removes the PID file.

status: Prints whether a gym server is running, with its PID and port.

All commands assume the repo root as the working directory.
"""

import argparse
import os
import subprocess
import sys
import time

PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        ".gym_server.pid")
SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "autoplay_server.py")


def find_gym_pids():
    """Return a list of PIDs for running autoplay_server.py processes.

    Uses PowerShell on Windows (wmic is not available on newer Windows
    builds), falls back to pgrep on Unix.
    """
    pids = []
    if sys.platform == "win32":
        try:
            ps_cmd = (
                "Get-CimInstance Win32_Process "
                "-Filter \"Name='python.exe'\" "
                "| Where-Object { $_.CommandLine -like '*autoplay_server*' } "
                "| Select-Object -ExpandProperty ProcessId"
            )
            out = subprocess.check_output(
                ["powershell", "-Command", ps_cmd],
                stderr=subprocess.DEVNULL, text=True)
            for line in out.strip().splitlines():
                line = line.strip()
                if line.isdigit():
                    pids.append(int(line))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    else:
        try:
            out = subprocess.check_output(
                ["pgrep", "-f", "autoplay_server.py"],
                stderr=subprocess.DEVNULL, text=True)
            for line in out.strip().splitlines():
                line = line.strip()
                if line.isdigit():
                    pids.append(int(line))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    return pids


def kill_pid(pid):
    """Kill a process by PID, cross-platform."""
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, check=True)
        else:
            os.kill(pid, 9)
    except (subprocess.CalledProcessError, ProcessLookupError):
        pass


def cmd_stop():
    pids = find_gym_pids()
    if not pids:
        print("No gym server running.")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        return
    for pid in pids:
        kill_pid(pid)
        print("Killed gym server PID %d." % pid)
    # Wait for the port to free
    time.sleep(1)
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    print("Gym server stopped.")


def cmd_status():
    pids = find_gym_pids()
    if not pids:
        print("No gym server running.")
        return
    saved_pid = None
    if os.path.exists(PID_FILE):
        with open(PID_FILE) as f:
            saved_pid = int(f.read().strip())
    for pid in pids:
        tag = " (tracked)" if pid == saved_pid else " (stale)"
        print("Gym server running, PID %d%s." % (pid, tag))


def cmd_start(args):
    # Kill any existing server first
    pids = find_gym_pids()
    if pids:
        for pid in pids:
            kill_pid(pid)
            print("Killed stale gym server PID %d." % pid)
        time.sleep(1)

    # Build the server command
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_story = os.path.join(here, "adventure_lovecraft.z5")

    cmd = [sys.executable, SERVER_SCRIPT,
           "--story", args.story or default_story,
           "--port", str(args.port)]
    if args.max_turns is not None:
        cmd += ["--max-turns", str(args.max_turns)]
    if args.seed is not None:
        cmd += ["--seed", str(args.seed)]

    # Start the server in the background
    log_path = os.path.join(os.path.dirname(PID_FILE), ".gym_server.log")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        cwd=here,
        text=True,
    )

    # Save the PID
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    print("Starting gym server (PID %d)..." % proc.pid)

    # Wait for "Listening on" in stderr, with timeout
    ready = False
    deadline = time.time() + 20
    while time.time() < deadline:
        line = proc.stderr.readline()
        if not line:
            if proc.poll() is not None:
                print("Gym server exited during startup.")
                sys.exit(1)
            continue
        line = line.strip()
        print("  " + line)
        if "Listening on" in line:
            ready = True
            break

    if not ready:
        print("Gym server did not report ready within 20s.")
        proc.terminate()
        sys.exit(1)

    print("Gym server ready on port %d." % args.port)


def main():
    ap = argparse.ArgumentParser(
        description="Start, stop, or check the Z-machine gym server.")
    sub = ap.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("start", help="start a fresh gym server")
    sp.add_argument("--story", default=None,
                    help="path to .z5 story file")
    sp.add_argument("--port", type=int, default=7777,
                    help="TCP port (default: 7777)")
    sp.add_argument("--max-turns", type=int, default=None,
                    help="end the game after N turns of input")
    sp.add_argument("--seed", type=int, default=None,
                    help="seed the PRNG for reproducible random output")

    sub.add_parser("stop", help="kill the running gym server")
    sub.add_parser("status", help="check if a gym server is running")

    args = ap.parse_args()

    if args.command == "start":
        cmd_start(args)
    elif args.command == "stop":
        cmd_stop()
    elif args.command == "status":
        cmd_status()


if __name__ == "__main__":
    main()
