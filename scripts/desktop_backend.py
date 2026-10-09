"""Run the local API for Infra Lens and stop it when the desktop app exits."""

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-pid", type=int, required=True)
    parser.add_argument("--backend", choices=["demo", "bge"], required=True)
    parser.add_argument("--rerank", action="store_true")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    command = [
        str(project / ".venv/bin/infra-rag"),
        "--backend",
        args.backend,
        "--data-dir",
        str(args.index),
    ]
    if args.rerank:
        command.append("--rerank")
    command.extend(["serve", "--port", str(args.port)])
    server = subprocess.Popen(command, cwd=project)
    stopping = False

    def request_stop(_signum, _frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    try:
        while not stopping and server.poll() is None:
            if os.getppid() != args.parent_pid:
                break
            time.sleep(0.3)
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()
    return server.returncode or 0


if __name__ == "__main__":
    sys.exit(main())
