#!/usr/bin/env python3

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from score_summary import score_summary
from calculate_abstraction import LocalCodeGenerator
from calculate_fluency import FluencyScorer

MODELS_DIR = Path(os.environ.get("SONAR_MODELS_DIR", SCRIPT_DIR / "models"))

GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY")
GEMINI_PROJECT  = os.environ.get("GEMINI_VERTEX_PROJECT", "your-gcp-project-id")
GEMINI_LOCATION = os.environ.get("GEMINI_VERTEX_LOCATION", "us-central1")
GEMINI_MODEL    = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

KIMI_API_KEY  = os.environ.get("KIMI_API_KEY")
KIMI_BASE_URL = os.environ.get("KIMI_BASE_URL", "https://api.moonshot.ai/v1")
KIMI_MODEL    = os.environ.get("KIMI_MODEL", "kimi-k2")

_FEW_SHOT_EX1_CODE = '''\
def has_duplicates(lst):
    return len(lst) != len(set(lst))
'''
_FEW_SHOT_EX1_SUMMARY = "Returns True if the list contains any duplicate elements, False otherwise."

_FEW_SHOT_EX2_CODE = '''\
def choose_num(x, y):
    if x > y:
        return -1
    if y % 2 == 0:
        return y
    if x == y:
        return -1
    return y - 1
'''
_FEW_SHOT_EX2_SUMMARY = (
    "Returns the largest even integer in the closed range [x, y], "
    "or -1 if no such integer exists."
)

PROMPTS = {
    "Vanilla": (
        "Summarize the following Python function using natural langauge. "
        "\n\n{code}"
    ),
    "dim_aware": (
        "Summarize the following Python function in natural language.\n\n"
        "Your summary should satisfy all four qualities simultaneously:\n"
        "- Correctness: accurately describe the behavior of the function.\n"
        "- Fluency: be grammatically correct, clear, and naturally readable.\n"
        "- Conciseness: should avoid redundancy.\n"
        "- Abstraction: should not leak implementation details\n\n"
        "{code}"
    ),
    "few_shot": (
        "Summarize the following Python function in natural language.\n\n"
        "Here are two examples:\n\n"
        "Example 1:\n"
        "```python\n"
        f"{_FEW_SHOT_EX1_CODE}"
        "```\n"
        f"Summary: {_FEW_SHOT_EX1_SUMMARY}\n\n"
        "Example 2:\n"
        "```python\n"
        f"{_FEW_SHOT_EX2_CODE}"
        "```\n"
        f"Summary: {_FEW_SHOT_EX2_SUMMARY}\n\n"
        "Now summarize this function:\n"
        "```python\n"
        "{code}\n"
        "```\n"
        "Summary:"
    ),
}

COMPRESS_PROMPT = (
    "Compress the following function summary into a shorter version, "
    "while retaining all behavioral information in the summary. "
    "If the summary cannot be compressed, return the original summary as output.\n\n"
    "Original summary: {summary}"
)

_PREAMBLE_RE = re.compile(
    r'^(?:(?:Sure|Certainly|Of course|Absolutely|Great)[!,]?\s+)?'
    r"(?:Here[’']s|Here is|Below is|Let[’']s|Let me)[^:\n]*:\s*\n+",
    re.IGNORECASE,
)
_HEADER_RE = re.compile(r'^(?:---+\s*\n+|#{1,4}\s+[^\n]+\n+|\*\*[^*\n]+\*\*\s*:?\s*\n+)+')


def _clean_summary(text: str) -> str:
    m = _PREAMBLE_RE.match(text)
    if m:
        text = text[m.end():]
    text = _HEADER_RE.sub("", text)
    return text.strip()


def _extract_code(raw: str, func_sig: str = "") -> str:
    text = raw.strip()
    text = re.sub(r"```python\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()
    fn = re.search(r"(def\s+\S+\(.*)", text, re.S)
    if fn:
        text = fn.group(1)
    lines, result, found, depth = text.split("\n"), [], False, 0
    for line in lines:
        s = line.rstrip()
        if s.startswith("def "):
            if found and depth == 0:
                break
            found = True
        elif found and depth == 0 and s and not s[0].isspace():
            break
        if found:
            depth += s.count("(") - s.count(")")
            depth = max(0, depth)
        result.append(line)
    code = "\n".join(result).rstrip()
    if not code or not code.lstrip().startswith("def "):
        code = func_sig + "\n    pass" if func_sig else "def _empty():\n    pass"
    return code


class GeminiModel:
    name = "gemini"

    def __init__(self):
        import google.genai as genai
        if GEMINI_API_KEY:
            self._client = genai.Client(api_key=GEMINI_API_KEY)
        else:
            self._client = genai.Client(vertexai=True, project=GEMINI_PROJECT, location=GEMINI_LOCATION)

    def _call(self, contents: str, retries: int = 5, call_timeout: int = 120) -> str:
        import concurrent.futures
        delay = 30
        for attempt in range(retries):
            try:
                ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                fut = ex.submit(self._client.models.generate_content, model=GEMINI_MODEL, contents=contents)
                try:
                    return fut.result(timeout=call_timeout).text
                except concurrent.futures.TimeoutError:
                    ex.shutdown(wait=False)
                    raise TimeoutError(f"[gemini] call timed out after {call_timeout}s")
                finally:
                    ex.shutdown(wait=False)
            except TimeoutError:
                raise
            except Exception as e:
                if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)) and attempt < retries - 1:
                    time.sleep(delay)
                    delay = min(delay * 2, 300)
                else:
                    raise

    def summarize(self, code: str, prompt: str) -> str:
        return _clean_summary(self._call(prompt.format(code=code)))

    def generate(self, summary: str, func_sig: str) -> str:
        from calculate_abstraction import CODE_GEN_SYSTEM
        prompt = f"{CODE_GEN_SYSTEM}\n\nSummary: {summary}\nFunction signature:\n{func_sig}\n\nOutput only code."
        return _extract_code(self._call(prompt), func_sig=func_sig)

    def compress(self, summary: str) -> str:
        return _clean_summary(self._call(COMPRESS_PROMPT.format(summary=summary), call_timeout=240))

    def unload(self):
        pass


class KimiModel:
    name = "kimi"

    def __init__(self):
        if not KIMI_API_KEY:
            raise RuntimeError("KIMI_API_KEY not set")
        import openai
        self._client = openai.OpenAI(base_url=KIMI_BASE_URL, api_key=KIMI_API_KEY)

    def _chat(self, messages: List[Dict]) -> str:
        stream = self._client.chat.completions.create(model=KIMI_MODEL, messages=messages, stream=True)
        content = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                content += delta
        return content

    def summarize(self, code: str, prompt: str) -> str:
        return _clean_summary(self._chat([{"role": "user", "content": prompt.format(code=code)}]))

    def unload(self):
        pass


class InstructLocalModel:
    def __init__(self, name: str, path: Path):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.name = name
        self._tok = AutoTokenizer.from_pretrained(str(path))
        major, _ = torch.cuda.get_device_capability() if torch.cuda.is_available() else (0, 0)
        dtype = torch.bfloat16 if major >= 8 else torch.float16
        self._mdl = AutoModelForCausalLM.from_pretrained(str(path), torch_dtype=dtype, device_map="auto")
        if self._tok.pad_token is None and self._tok.eos_token is not None:
            self._tok.pad_token = self._tok.eos_token
        self._mdl.eval()

    def summarize(self, code: str, prompt: str) -> str:
        import torch
        messages = [{"role": "user", "content": prompt.format(code=code)}]
        if hasattr(self._tok, "apply_chat_template"):
            prompt = self._tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            prompt = f"<user>\n{messages[0]['content']}\n<assistant>\n"
        inputs = self._tok(prompt, return_tensors="pt", truncation=True).to(self._mdl.device)
        plen = inputs["input_ids"].shape[1]
        with torch.inference_mode():
            out = self._mdl.generate(
                **inputs, max_new_tokens=512, do_sample=False,
                pad_token_id=self._tok.pad_token_id, eos_token_id=self._tok.eos_token_id,
            )
        raw = self._tok.decode(out[0][plen:], skip_special_tokens=True).strip()
        return _clean_summary(raw)

    def unload(self):
        import gc, torch
        del self._mdl, self._tok
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


class CompletionLocalModel:
    _PROMPT = (
        "# Python function:\n{code}\n\n"
        "# One-paragraph natural language summary of what this function does:\n#"
    )

    def __init__(self, name: str, path: Path):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.name = name
        self._tok = AutoTokenizer.from_pretrained(str(path))
        major, _ = torch.cuda.get_device_capability() if torch.cuda.is_available() else (0, 0)
        dtype = torch.bfloat16 if major >= 8 else torch.float16
        self._mdl = AutoModelForCausalLM.from_pretrained(str(path), torch_dtype=dtype, device_map="auto")
        if self._tok.pad_token is None and self._tok.eos_token is not None:
            self._tok.pad_token = self._tok.eos_token
        self._mdl.eval()

    def summarize(self, code: str, prompt: str) -> str:
        import torch
        fixed_prompt = self._PROMPT.format(code=code)
        inputs = self._tok(fixed_prompt, return_tensors="pt", truncation=True).to(self._mdl.device)
        plen = inputs["input_ids"].shape[1]
        with torch.inference_mode():
            out = self._mdl.generate(
                **inputs, max_new_tokens=128, do_sample=False,
                pad_token_id=self._tok.pad_token_id, eos_token_id=self._tok.eos_token_id,
            )
        raw = self._tok.decode(out[0][plen:], skip_special_tokens=True).strip()
        return raw.split("\n\n")[0].strip().lstrip("# ").strip()

    def unload(self):
        import gc, torch
        del self._mdl, self._tok
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


class Seq2SeqLocalModel:
    def __init__(self, name: str, path: Path):
        import torch
        from tokenizers import ByteLevelBPETokenizer
        from transformers import PreTrainedTokenizerFast, T5ForConditionalGeneration
        self.name = name
        bpe = ByteLevelBPETokenizer(str(path / "vocab.json"), str(path / "merges.txt"))
        self._tok = PreTrainedTokenizerFast(
            tokenizer_object=bpe, bos_token="<s>", eos_token="</s>", unk_token="<unk>",
            sep_token="</s>", cls_token="<s>", pad_token="<pad>", mask_token="<mask>", model_max_length=512,
        )
        self._mdl = T5ForConditionalGeneration.from_pretrained(str(path)).to(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self._mdl.eval()

    def summarize(self, code: str, prompt: str) -> str:
        import torch
        token_ids = self._tok.encode(code)[:512]
        inputs = {
            "input_ids": torch.tensor([token_ids]).to(self._mdl.device),
            "attention_mask": torch.ones(1, len(token_ids), dtype=torch.long).to(self._mdl.device),
        }
        with torch.inference_mode():
            out = self._mdl.generate(
                **inputs, max_length=64, num_beams=4, repetition_penalty=2.5,
                decoder_start_token_id=self._mdl.config.decoder_start_token_id,
            )
        return self._tok.decode(out[0], skip_special_tokens=True).strip()

    def unload(self):
        import gc, torch
        del self._mdl, self._tok
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


MODEL_REGISTRY = {
    "gemini":     {"kind": "gemini"},
    "kimi":       {"kind": "kimi"},
    "olmo":       {"kind": "instruct",   "path": MODELS_DIR / "OLMo-3.1-32B-Instruct"},
    "qwen":       {"kind": "instruct",   "path": MODELS_DIR / "qwen2_5_coder_32b"},
    "codegemma":  {"kind": "instruct",   "path": MODELS_DIR / "codegemma-7b-it"},
    "mistral":    {"kind": "instruct",   "path": MODELS_DIR / "Mistral-7B-Instruct-v0.3"},
    "codellama":  {"kind": "instruct",   "path": MODELS_DIR / "CodeLlama-13B-Instruct"},
    "codestral":  {"kind": "instruct",   "path": MODELS_DIR / "Codestral-22B"},
    "phi35_mini": {"kind": "instruct",   "path": MODELS_DIR / "Phi-3.5-mini-instruct"},
    "starcoder2": {"kind": "completion", "path": MODELS_DIR / "starcoder2-3b"},
    "codet5_sum": {"kind": "seq2seq",    "path": MODELS_DIR / "codet5-base-sum-python"},
}

ABSTRACTION_POOL = ["gemini", "olmo", "qwen"]


def get_model(name: str):
    cfg = MODEL_REGISTRY[name]
    kind = cfg["kind"]
    if kind == "gemini":
        return GeminiModel()
    if kind == "kimi":
        return KimiModel()
    if kind == "instruct":
        return InstructLocalModel(name, cfg["path"])
    if kind == "completion":
        return CompletionLocalModel(name, cfg["path"])
    if kind == "seq2seq":
        return Seq2SeqLocalModel(name, cfg["path"])
    raise ValueError(f"unknown model kind: {kind}")


def _abstraction_generator(name: str, judge: GeminiModel):
    if name == "gemini":
        return judge
    cfg = MODEL_REGISTRY[name]
    if cfg["kind"] != "instruct":
        raise ValueError(f"{name} can't be used as an abstraction generator (kind={cfg['kind']})")
    return LocalCodeGenerator(cfg["path"])


def _summarize_all(
    entries: List[Tuple[str, str]],
    models: List[str],
    strategy: str,
) -> Dict[str, Dict[str, str]]:
    prompt = PROMPTS[strategy]
    summaries: Dict[str, Dict[str, str]] = {task_id: {} for task_id, _ in entries}
    for name in models:
        summarizer = get_model(name)
        for task_id, code in entries:
            summaries[task_id][name] = summarizer.summarize(code, prompt)
        summarizer.unload()
    return summaries


def _score_all(
    entries: List[Tuple[str, str]],
    summaries: Dict[str, Dict[str, str]],
    models: List[str],
    abstraction_pool: List[str],
) -> Dict[str, Dict]:
    judge = GeminiModel()
    generators = [_abstraction_generator(name, judge) for name in abstraction_pool]
    fluency_scorer = FluencyScorer()

    results: Dict[str, Dict] = {task_id: {} for task_id, _ in entries}
    for task_id, code in entries:
        for name in models:
            summary = summaries[task_id][name]
            correctness, abstraction, conciseness, fluency = score_summary(
                summary=summary,
                code=code,
                task_id=task_id,
                code_generator=judge.generate,
                compressor=judge.compress,
                generators=generators,
                fluency_scorer=fluency_scorer,
            )
            results[task_id][name] = {
                "summary":     summary,
                "correctness": correctness,
                "abstraction": abstraction,
                "conciseness": conciseness,
                "fluency":     fluency,
            }

    for g in generators:
        if g is not judge:
            g.unload()

    return results


DATASETS_DIR = SCRIPT_DIR / "datasets"


def _load_entries():
    for path in sorted(DATASETS_DIR.glob("*.jsonl")):
        with path.open(encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    yield r["task_id"], r["code"]


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", choices=list(PROMPTS), default="Vanilla",
                        help="Summarization prompting strategy")
    parser.add_argument("--models", nargs="+", choices=list(MODEL_REGISTRY), default=None,
                        help="Which models to generate+score summaries with (default: all 11)")
    args = parser.parse_args()

    models = args.models if args.models is not None else list(MODEL_REGISTRY)
    entries = list(_load_entries())

    summaries = _summarize_all(entries, models, args.strategy)
    results = _score_all(entries, summaries, models, ABSTRACTION_POOL)

    results_dir = SCRIPT_DIR / "results"
    results_dir.mkdir(exist_ok=True)
    out_path = results_dir / f"results_{args.strategy}.jsonl"
    with out_path.open("w", encoding="utf-8") as out:
        for task_id, _ in entries:
            out.write(json.dumps({"task_id": task_id, "results": results[task_id]}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
