#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON=${PYTHON:-python}
MODEL=${MODEL:?set MODEL to the local qwen2_5_coder_32b weights path}

"$PYTHON" -u "$DIR/run_pipeline.py" \
    --model "$MODEL" \
    --summaries "$DIR/../summary_pool.jsonl" \
    --out "$DIR/optimization_qwen.jsonl"
