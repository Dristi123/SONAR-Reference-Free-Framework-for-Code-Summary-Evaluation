#!/usr/bin/env bash
set -e

# Rebuild the prompting-strategy bar chart from common_pool_for_all_prompting.jsonl
python3 generate_bar_chart.py

# Rebuild the model-level spider chart from vanilla_scores.jsonl
python3 generate_spider_chart.py
