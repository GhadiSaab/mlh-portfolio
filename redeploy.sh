#!/bin/bash
set -e
PROJECT_DIR="/opt/mlh-portfolio"
cd "$PROJECT_DIR"
git fetch
git reset origin/main --hard
uv sync
systemctl restart myportfolio
echo "Redeploy complete."
