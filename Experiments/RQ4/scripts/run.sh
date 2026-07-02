#!/usr/bin/env bash
set -e

# Rebuild the sensitivity table from conciseness_correctness_scores.jsonl
python3 create_table.py
