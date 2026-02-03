#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --user|--repo [--path <skills_dir>]"
  echo "  --user  Install to ~/.codex/skills"
  echo "  --repo  Install to ./.codex/skills in current project"
  echo "  --path  Override destination skills directory"
}

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

DEST=""
MODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)
      MODE="user"
      shift
      ;;
    --repo)
      MODE="repo"
      shift
      ;;
    --path)
      DEST="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1"
      usage
      exit 1
      ;;
  esac
 done

if [[ -z "$DEST" ]]; then
  if [[ "$MODE" == "user" ]]; then
    DEST="$HOME/.codex/skills"
  elif [[ "$MODE" == "repo" ]]; then
    DEST=".codex/skills"
  else
    echo "Choose --user or --repo"
    exit 1
  fi
fi

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/skills/promptrefinelab"

mkdir -p "$DEST"
rm -rf "$DEST/promptrefinelab"
cp -R "$SRC_DIR" "$DEST/"

echo "Installed promptrefinelab skill to: $DEST/promptrefinelab"
