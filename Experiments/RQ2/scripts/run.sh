#!/usr/bin/env bash
set -e

# Builds Table III (partial Spearman correlations between each method and downstream performance,
# with 95% bootstrap CIs) from the per-model results shipped in this repo:
#   retrieval/mrr_scores_rerun.csv, translation/, optimization/, oracle_gen/*.jsonl, summary_pool.jsonl,
#   and the LLM-judge scores in ../../Major_Revision/LLM_Judges/scripts/judge_scores.csv.
# Output: ../../Major_Revision/Association/results/correlation_table.csv. No GPU or API keys needed.
cd ../../Major_Revision/Association/scripts
python3 create_table.py
cd - > /dev/null

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
# Retrieval MRR scores (retrieval/mrr_scores_rerun.csv) are shipped as computed; their embedding caches are not included.
