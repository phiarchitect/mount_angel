#!/usr/bin/env bash
# Headless FreeCAD Runner for Mount Angel Library
# Executes FreeCAD scripts offscreen via xvfb-run with PYTHONPATH set.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FREECAD_APPIMAGE="/home/phi/AppImages/FreeCAD_1.1.3-Linux-x86_64-py311.AppImage"

if [ ! -f "$FREECAD_APPIMAGE" ]; then
    echo "ERROR: FreeCAD AppImage not found at: $FREECAD_APPIMAGE" >&2
    exit 1
fi

if [ $# -lt 1 ]; then
    echo "Usage: $0 <script_path>" >&2
    echo "Example: $0 src/phiarchitect/mountangel/skeleton.py" >&2
    exit 1
fi

SCRIPT_PATH="$1"
if [[ ! "$SCRIPT_PATH" = /* ]]; then
    SCRIPT_PATH="${REPO_ROOT}/${SCRIPT_PATH}"
fi

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "ERROR: Script file not found: $SCRIPT_PATH" >&2
    exit 1
fi

export PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH:-}"

exec xvfb-run -a "$FREECAD_APPIMAGE" -c "import sys; sys.path.insert(0, '${REPO_ROOT}/src'); __file__='${SCRIPT_PATH}'; exec(open(__file__).read())"
