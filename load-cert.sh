#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.venv/bin/activate"
PYTHON_SCRIPT="$SCRIPT_DIR/load-cert.py"

if [[ ! -f "$VENV_PATH" ]]; then
    echo "Virtual environment not found: $VENV_PATH" >&2
    exit 1
fi

if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Python script not found: $PYTHON_SCRIPT" >&2
    exit 1
fi

cd "$SCRIPT_DIR" || exit 1
# shellcheck source=/dev/null
source "$VENV_PATH"
python3 "$PYTHON_SCRIPT" "$@"
status=$?
deactivate 2>/dev/null || true
exit $status