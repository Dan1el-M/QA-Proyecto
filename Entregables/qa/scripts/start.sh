#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
source qa/scripts/env.sh
export RAILS_ENV=test
ruby qa/scripts/prepare.rb "${1:-base}"
exec ruby qa/scripts/server.rb
