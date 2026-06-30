#!/usr/bin/env bash
set -euo pipefail

curl -X POST http://127.0.0.1:8717/reason \
  -H "Content-Type: application/json" \
  -d '{"message":"Map remote work against operational overhead and knowledge siloing.","operator":"coordinate_game"}'
