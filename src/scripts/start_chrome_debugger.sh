#!/bin/bash

# This script starts Google Chrome with remote debugging enabled on a port
# and uses a dedicated user data directory, with values loaded from .env.

# Load environment variables from .env if it exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

CHROME_PATH="${CHROME_PATH:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
DEBUG_PORT="${CHROME_DEBUGGING_PORT:-9222}"
USER_DATA_DIR="${CHROME_USER_DATA_DIR:-/tmp/chrome-debug}"

# Check if Chrome is already running with the debugging port
if lsof -i :$DEBUG_PORT | grep LISTEN > /dev/null; then
  echo "Chrome is already running with remote debugging on port $DEBUG_PORT."
  exit 0
fi

echo "Starting Chrome with remote debugging on port $DEBUG_PORT..."
"$CHROME_PATH" --remote-debugging-port=$DEBUG_PORT --user-data-dir="$USER_DATA_DIR" &

echo "Chrome started. You can now connect Selenium or other tools to localhost:$DEBUG_PORT"
