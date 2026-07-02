#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON=${PYTHON:-python}
MODEL=${MODEL:?set MODEL to the local OLMo-3.1-32B-Instruct weights path}

"$PYTHON" -u "$DIR/run_pipeline.py" \
    --model "$MODEL" \
    --summaries "$DIR/../summary_pool.jsonl" \
    --out "$DIR/optimization_olmo.jsonl"
