#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-dist}"
SKILL_NAME="promptrefinelab"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/skills/$SKILL_NAME"

mkdir -p "$OUT_DIR"

ARCHIVE="$OUT_DIR/$SKILL_NAME.skill"

if [[ -f "$ARCHIVE" ]]; then
  rm -f "$ARCHIVE"
fi

( cd "$(dirname "$SRC_DIR")" && zip -r "$(pwd)/$ARCHIVE" "$SKILL_NAME" >/dev/null )

echo "Packaged: $ARCHIVE"
