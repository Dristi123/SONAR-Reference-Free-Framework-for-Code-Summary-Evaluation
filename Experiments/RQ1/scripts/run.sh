#!/usr/bin/env bash
set -e

# 1) Derive SONAR's per-summary scores from rq1_data.jsonl
python3 calculate_scores.py

# 2) Build the agreement table from sonar_scores.jsonl + the cached LLM scores shipped with this repo
python3 create_table.py

# 3) (Optional) To refresh the cached LLM scores instead of using the ones shipped here:
#    - Claude: export ANTHROPIC_API_KEY=...
#    - Gemini: export GEMINI_VERTEX_PROJECT=... and authenticate via gcloud application-default login
# python3 rq1_llm_only_baseline.py --scorer claude
# python3 rq1_llm_only_baseline.py --scorer gemini

# 4) Rebuild the agreement table using the fresh scores
# python3 create_table.py


