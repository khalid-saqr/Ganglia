#!/usr/bin/env bash
set -euo pipefail

curl -X POST http://127.0.0.1:8717/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"ganglia/auto","messages":[{"role":"user","content":"Stress-test my SaaS pricing model."}]}'
