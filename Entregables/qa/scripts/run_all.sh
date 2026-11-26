#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
source qa/scripts/env.sh
exec python qa/scripts/run_all.py "$@"
