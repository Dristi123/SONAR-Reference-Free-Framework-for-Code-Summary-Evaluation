#!/usr/bin/env bash
set -e

# Builds the correlation table from the per-model results already shipped in
# this repo (translation/, optimization/, oracle_gen/*.jsonl, retrieval/retrieval_metrics.jsonl).
# No GPU or API keys needed for this step.
python3 create_correlation_table.py

# (Optional) Partial-Spearman table (each SONAR dim controlled for the other 3)
# -> ../results/correlation_partial.csv
# python3 create_correlation_table.py --partial

# ---------------------------------------------------------------------------
# (Optional) To regenerate the per-model results from scratch instead of using
# the shipped data above:
#
# 1) GPU + local weights for qwen/olmo -- point MODEL= at them below.
#
# 2) Gemini. Pick one:
#      Option A, API key:
#        get one at https://aistudio.google.com/apikey, then:
#        export GEMINI_API_KEY=your-api-key
#      Option B, Vertex AI:
#        export GEMINI_VERTEX_PROJECT=your-gcp-project-id
#        export GEMINI_VERTEX_LOCATION=us-central1   # optional, this is the default
#        gcloud auth application-default login
#
# 3) javatuples-1.2.jar (translation only, to compile MultiPL-E-generated
#    Java test harnesses): download org.javatuples:javatuples:1.2 from Maven
#    Central and place it at translation/../MultiPL-E/javatuples-1.2.jar
#
# Then run:
#   cd translation
#   MODEL=/path/to/qwen2_5_coder_32b        ./run_full_qwen.sh
#   MODEL=/path/to/OLMo-3.1-32B-Instruct    ./run_full_olmo.sh
#   ./run_full_gemini.sh
#   cd ../optimization
#   MODEL=/path/to/qwen2_5_coder_32b        ./run_full_qwen.sh
#   MODEL=/path/to/OLMo-3.1-32B-Instruct    ./run_full_olmo.sh
#   ./run_full_gemini.sh
#   cd ../oracle_gen
#   MODEL=/path/to/qwen2_5_coder_32b        ./run_full_qwen.sh
#   MODEL=/path/to/OLMo-3.1-32B-Instruct    ./run_full_olmo.sh
#   ./run_full_gemini.sh
#   cd ..
#
# Then re-run this script to rebuild the table from the fresh data.
