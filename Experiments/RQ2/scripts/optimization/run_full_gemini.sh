#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON=${PYTHON:-python}
MAX_ROWS=${MAX_ROWS:-1085}

"$PYTHON" -u "$DIR/run_pipeline.py" \
    --model gemini \
    --summaries "$DIR/../summary_pool.jsonl" \
    --out "$DIR/optimization_gemini.jsonl" \
    --max-rows "$MAX_ROWS"
