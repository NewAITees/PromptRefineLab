from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run prl CLI with a config file")
    parser.add_argument("command", choices=["validate", "evaluate", "optimize"])
    parser.add_argument("config", type=Path)
    parser.add_argument("--steps", type=int, default=5)
    args = parser.parse_args()

    if not shutil.which("prl"):
        print("prl CLI not found on PATH. Install the package first.")
        return 2

    cmd = ["prl", args.command, str(args.config)]
    if args.command == "optimize":
        cmd.extend(["--steps", str(args.steps)])

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except OSError as exc:
        print(f"Failed to run prl: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
