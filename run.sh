#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"
source venv/bin/activate

# Start dev server in background
python3 dev/server.py &
SERVER_PID=$!
sleep 1

# Run exporter (Ctrl+C to stop)
trap "kill $SERVER_PID 2>/dev/null" EXIT
cd src/exporter-ecoadapt
python3 exporter-ecoadapt.py
