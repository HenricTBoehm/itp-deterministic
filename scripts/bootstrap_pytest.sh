#!/bin/sh
set -eu

PYTHON="${PYTHON:-python3.11}"
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BOOTSTRAP_DIR="${BOOTSTRAP_DIR:-/tmp/opencode/itp-python-bootstrap}"
VENV="${VENV:-/tmp/opencode/itp-pytest-venv}"

mkdir -p "$BOOTSTRAP_DIR"
curl -fsSLo "$BOOTSTRAP_DIR/get-pip.py" https://bootstrap.pypa.io/get-pip.py
"$PYTHON" "$BOOTSTRAP_DIR/get-pip.py" --target "$BOOTSTRAP_DIR/pip"
PYTHONPATH="$BOOTSTRAP_DIR/pip" "$PYTHON" -m pip install --target "$BOOTSTRAP_DIR/virtualenv" 'virtualenv==21.15.6'
PYTHONPATH="$BOOTSTRAP_DIR/virtualenv" "$PYTHON" -m virtualenv "$VENV"
"$VENV/bin/pip" install -e "$ROOT[test]"
echo "pytest environment: $VENV"
