#!/usr/bin/env bash
# Launch Wildlife Camouflage AI Mission Control Dashboard
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

echo "======================================================================"
echo "   Starting Wildlife Camouflage AI Mission Control Dashboard...      "
echo "======================================================================"
echo "Open your browser at: http://localhost:5000"
echo "======================================================================"

python3 "${SCRIPT_DIR}/start_dashboard.py"
