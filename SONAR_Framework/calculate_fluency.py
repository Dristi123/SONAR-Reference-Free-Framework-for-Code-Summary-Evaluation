#!/usr/bin/env python3

import math
from typing import Dict, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

GPT2_MODEL = "gpt2"


class FluencyScorer:

    def __init__(self, model_name: str = GPT2_MODEL):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, use_safetensors=True
        )
        self.model.eval()
        self.model.to(self.device)

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def compute_perplexity(self, text: str) -> float:
        encodings = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=1024
        )
        input_ids = encodings.input_ids.to(self.device)

        if input_ids.size(1) < 2:
            return float("inf")

        with torch.no_grad():
            outputs = self.model(input_ids, labels=input_ids)
            neg_log_likelihood = outputs.loss

        ppl = math.exp(neg_log_likelihood.item())
        return ppl


    PPL_MIN = 8
    PPL_MAX = 500

    @staticmethod
    def ppl_to_fluency(ppl: float) -> float:
        if ppl == float("inf") or ppl <= 0:
            return 0.0
        log_max = math.log(FluencyScorer.PPL_MAX)
        log_min = math.log(FluencyScorer.PPL_MIN)
        score = (log_max - math.log(ppl)) / (log_max - log_min)
        return max(0.0, min(1.0, score))

    def score(self, text: str) -> Dict[str, float]:
        ppl = self.compute_perplexity(text)
        fluency = self.ppl_to_fluency(ppl)
        return {
            "perplexity": round(ppl, 2),
            "fluency": round(fluency, 4),
        }


def score_fluency(summary: str, scorer: Optional[FluencyScorer] = None) -> float:
    _scorer = scorer if scorer is not None else FluencyScorer()
    text = preprocess_summary(summary)
    return _scorer.score(text)["fluency"]


def preprocess_summary(summary: str) -> str:
    return summary.strip()
