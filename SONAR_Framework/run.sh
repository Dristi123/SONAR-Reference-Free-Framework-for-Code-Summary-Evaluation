#!/usr/bin/env bash

# --- Setup ------------------------------------------------------------------
# 1) Gemini (required -- judge for correctness/conciseness). Pick one:
#      Option A, API key:
#        get one at https://aistudio.google.com/apikey, then:
#        export GEMINI_API_KEY=your-api-key
#      Option B, Vertex AI:
#        export GEMINI_VERTEX_PROJECT=your-gcp-project-id
#        export GEMINI_VERTEX_LOCATION=us-central1   # optional, this is the default
#        gcloud auth application-default login
#
# 2) Olmo + Qwen (required -- default abstraction pool, alongside Gemini):
#      download the weights (e.g. from Hugging Face), then:
#      export SONAR_MODELS_DIR=/path/to/downloaded/model/weights
#
# 3) Joern + Java 17 (required -- calculate_abstraction.py builds code
#    property graphs with it for abstraction diversity scoring):
#      install Joern (https://joern.io) to ~/joern/joern-cli
#      put Java 17 on PATH, or: export JAVA17_HOME=/path/to/java17
# ------------------------------------------------------------------------------

# 1) Generate summaries and score them on all 4 SONAR dimensions.
#    Datasets included: HE (164), MBPP (112), BigCodeBench (112), TheVault (112).
#    --models   : space-separated, e.g. --models gemini kimi olmo
#                 choices: gemini kimi olmo qwen codegemma mistral codellama
#                          codestral phi35_mini starcoder2 codet5_sum
#                 omit --models entirely to run all 11 (the default)
#    --strategy : Vanilla | dim_aware | few_shot  -- omit for the default, Vanilla
python3 generate_and_score.py --models gemini --strategy Vanilla

# 2) Results are written to results/results_<strategy>.jsonl
