#!/bin/bash
set -e

PROJECT_DIR="./"
SESSION_NAME="flask-app"

tmux kill-server 2>/dev/null || true

cd "$PROJECT_DIR"
git fetch
git reset origin/main --hard

# 4. Install dependencies (uv sync creates/updates the venv automatically)
uv sync

tmux new-session -d -s "$SESSION_NAME" \
  "cd $PROJECT_DIR && uv run flask run --host 0.0.0.0 --port 5000"

echo "Redeploy complete. Session '$SESSION_NAME' is running."
