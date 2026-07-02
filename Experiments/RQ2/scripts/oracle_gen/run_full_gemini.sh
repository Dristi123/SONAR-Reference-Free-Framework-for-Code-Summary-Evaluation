#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON=${PYTHON:-python}

"$PYTHON" -u "$DIR/run_pipeline.py" \
    --model gemini \
    --model-name gemini \
    --out-dir "$DIR" \
    --n-asserts 10
