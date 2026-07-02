#!/usr/bin/env python3

import ast
import gc
import html
import io
import json
import keyword
import os
import re
import subprocess
import sys
import tempfile
import tokenize
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


JOERN_CLI_DIR = Path.home() / "joern" / "joern-cli"
JOERN_PARSE   = str(JOERN_CLI_DIR / "joern-parse")
JOERN_EXPORT  = str(JOERN_CLI_DIR / "joern-export")
JOERN_TIMEOUT = 120

_JAVA17_BIN = Path(os.environ.get("JAVA17_HOME", "/usr/lib/jvm/java-17"))
_JOERN_ENV  = os.environ.copy()
_JOERN_ENV["PATH"]      = str(_JAVA17_BIN) + ":" + str(JOERN_CLI_DIR) + ":" + _JOERN_ENV.get("PATH", "")
_JOERN_ENV["JAVA_HOME"] = str(_JAVA17_BIN.parent)


_PYTHON_KW   = set(keyword.kwlist)
_SKIP_TTYPES = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                tokenize.ENCODING, tokenize.INDENT, tokenize.DEDENT}


def _sig_tokens(func_sig: str) -> Set[str]:
    try:
        return {tok.string
                for tok in tokenize.generate_tokens(io.StringIO(func_sig).readline)
                if tok.type == tokenize.NAME}
    except Exception:
        return set(re.findall(r'\b\w+\b', func_sig))


def _token_list(code: str, exclude: Set[str]) -> List[str]:
    drop = _PYTHON_KW | exclude
    try:
        return [tok.string
                for tok in tokenize.generate_tokens(io.StringIO(code).readline)
                if tok.type not in _SKIP_TTYPES and tok.string not in drop]
    except Exception:
        return [t for t in re.findall(r'\w+|[^\w\s]', code) if t not in drop]


def _ast_jaccard(a: str, b: str) -> float:
    try:
        n1 = {type(n).__name__ for n in ast.walk(ast.parse(a))}
        n2 = {type(n).__name__ for n in ast.walk(ast.parse(b))}
        u  = len(n1 | n2)
        return len(n1 & n2) / u if u else 0.0
    except SyntaxError:
        return 0.0


def _strip_docstrings(code: str) -> str:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            if (node.body
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(getattr(node.body[0], 'value', None), ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body = node.body[1:] or [ast.Pass()]
    try:
        return ast.unparse(tree)
    except Exception:
        return code


def _token_bigram_jaccard(a: str, b: str, exclude: Set[str]) -> float:
    def bigrams(code):
        toks = _token_list(_strip_docstrings(code), exclude)
        return set(zip(toks, toks[1:])) if len(toks) >= 2 else set()
    ba, bb = bigrams(a), bigrams(b)
    u = len(ba | bb)
    return len(ba & bb) / u if u else 1.0


_NODE_PAT = re.compile(r'"(\d+)"\s*\[label\s*=\s*<([^,>]+)')
_EDGE_PAT = re.compile(r'"(\d+)"\s*->\s*"(\d+)"\s*(?:\[\s*label\s*=\s*"([^"]*)"\s*\])?')


def _node_map(content: str) -> Dict[str, str]:
    return {m.group(1): html.unescape(m.group(2)).strip()
            for m in _NODE_PAT.finditer(content)}


def _cpg_edges(dot_path: Path) -> Set[Tuple[str, str, str]]:
    content = dot_path.read_text(encoding="utf-8", errors="replace")
    nodes   = _node_map(content)
    edges: Set[Tuple[str, str, str]] = set()
    for m in _EDGE_PAT.finditer(content):
        s, t = m.group(1), m.group(2)
        if s not in nodes or t not in nodes:
            continue
        raw   = (m.group(3) or "").strip()
        etype = raw.split(":")[0].strip() if raw else "UNKNOWN"
        edges.add((nodes[s], etype, nodes[t]))
    return edges


def _find_dot(cpg_dir: Path, func_name: str) -> Optional[Path]:
    pat = re.compile(r'<METHOD,\s*\d+<BR/>' + re.escape(func_name) + r'>')
    for dot in cpg_dir.glob("*.dot"):
        if pat.search(dot.read_text(encoding="utf-8", errors="replace")):
            return dot
    return None


def _rename_fn(code: str, old: str, new: str) -> str:
    return re.sub(r'\bdef\s+' + re.escape(old) + r'\s*\(', f'def {new}(', code)


def _run_cmd(cmd: List[str]) -> bool:
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=_JOERN_ENV, timeout=JOERN_TIMEOUT)
        return r.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def _get_cpg_sets(codes: List[str], entry_point: str) -> List[Optional[Set]]:
    n    = len(codes)
    sets: List[Optional[Set]] = [None] * n
    with tempfile.TemporaryDirectory(prefix="joern_abs_") as td:
        src_dir = Path(td) / "src"
        cpg_bin = Path(td) / "batch.cpg"
        cpg_out = Path(td) / "cpg_export"
        src_dir.mkdir()
        gen_names = [f"gen_{i}" for i in range(n)]
        for i, (code, gname) in enumerate(zip(codes, gen_names)):
            (src_dir / f"{gname}.py").write_text(
                _rename_fn(code, entry_point, gname), encoding="utf-8")
        if not _run_cmd([JOERN_PARSE, str(src_dir), "--output", str(cpg_bin)]):
            return sets
        if _run_cmd([JOERN_EXPORT, str(cpg_bin), "--repr", "cpg14", "--out", str(cpg_out)]):
            for i, gname in enumerate(gen_names):
                dot = _find_dot(cpg_out, gname)
                if dot:
                    sets[i] = _cpg_edges(dot)
    return sets


def _jaccard(a: Set, b: Set) -> float:
    if not a and not b:
        return 1.0
    u = len(a | b)
    return len(a & b) / u if u else 0.0


def _entry_point(func_sig: str) -> str:
    m = re.search(r'def\s+(\w+)\s*\(', func_sig)
    return m.group(1) if m else "func"


def compute_diversity(codes: List[str], entry_point: str, func_sig: str) -> Dict[str, Any]:
    if len(codes) < 2:
        return {"diversity_score": 0.0, "mean_sim": 1.0,
                "n_valid_pairs": 0, "cpg_available": False}

    exclude  = _sig_tokens(func_sig)
    pairs    = list(combinations(range(len(codes)), 2))
    cpg_sets = _get_cpg_sets(codes, entry_point)
    valid    = [(i, j) for i, j in pairs if cpg_sets[i] and cpg_sets[j]]

    if valid:
        sims = [
            0.5 * _jaccard(cpg_sets[i], cpg_sets[j]) +
            0.5 * _token_bigram_jaccard(codes[i], codes[j], exclude)
            for i, j in valid
        ]
        cpg_available = True
        used_pairs    = valid
    else:
        sims = [
            0.5 * _ast_jaccard(codes[i], codes[j]) +
            0.5 * _token_bigram_jaccard(codes[i], codes[j], exclude)
            for i, j in pairs
        ]
        cpg_available = False
        used_pairs    = pairs

    mean_sim = sum(sims) / len(sims) if sims else 1.0
    return {
        "diversity_score": round(1.0 - mean_sim, 4),
        "mean_sim":        round(mean_sim, 4),
        "n_valid_pairs":   len(used_pairs),
        "cpg_available":   cpg_available,
    }


def score_abstraction(
    summary: str,
    func_sig: str,
    generators: List,
    n_samples: int = 3,
) -> float:
    ep    = _entry_point(func_sig)
    codes: List[str] = []
    for gen in generators:
        for _ in range(n_samples):
            codes.append(gen.generate(summary, func_sig))
    return compute_diversity(codes, ep, func_sig)["diversity_score"]


CODE_GEN_SYSTEM = (
    "You are a Python code generator. Given a function summary and its signature, "
    "produce a correct, complete Python function. "
    "Follow every algorithmic and structural detail mentioned in the summary exactly — "
    "these are strict requirements. "
    "Follow the variable names mentioned in the summary exactly. "
    "Where the summary leaves details unspecified, feel free to use your own approach and naming. "
    "Do not include docstrings or inline comments. Output only the code."
)


class LocalCodeGenerator:

    _SYSTEM = CODE_GEN_SYSTEM

    def __init__(self, model_path, max_new_tokens: int = 512):
        self.max_new_tokens = max_new_tokens
        self.model_name     = Path(model_path).name
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path, trust_remote_code=True, use_fast=False
        )
        if torch.cuda.is_available():
            major, _ = torch.cuda.get_device_capability()
            dtype = torch.bfloat16 if major >= 8 else torch.float16
        else:
            dtype = torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, dtype=dtype, device_map="auto",
            trust_remote_code=True,
        )
        if self.tokenizer.pad_token is None and self.tokenizer.eos_token is not None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.eval()

    def _prompt(self, summary: str, func_sig: str) -> str:
        user = (
            f"Summary: {summary}\n\n"
            f"Function signature:\n{func_sig}\n\n"
            "Output only the Python function code."
        )
        if hasattr(self.tokenizer, "apply_chat_template"):
            return self.tokenizer.apply_chat_template(
                [{"role": "system", "content": self._SYSTEM},
                 {"role": "user",   "content": user}],
                tokenize=False, add_generation_prompt=True,
            )
        return f"<system>\n{self._SYSTEM}\n</system>\n<user>\n{user}\n</user>\n<assistant>\n"

    @torch.inference_mode()
    def generate(self, summary: str, func_sig: str) -> str:
        prompt  = self._prompt(summary, func_sig)
        inputs  = self.tokenizer(prompt, return_tensors="pt",
                                 truncation=True, padding=True).to(self.model.device)
        plen    = inputs["input_ids"].shape[1]
        out     = self.model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=True,
            temperature=0.8,
            top_p=0.95,
            top_k=50,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        raw = self.tokenizer.decode(out[0][plen:], skip_special_tokens=True).strip()
        return _extract_code_local(raw, func_sig=func_sig)

    def unload(self):
        del self.model, self.tokenizer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


def _extract_code_local(raw: str, func_sig: str = "") -> str:
    text = raw.strip()
    text = re.sub(r"```python\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()
    fn   = re.search(r"(def\s+\S+\(.*)", text, re.S)
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
        if func_sig:
            code = func_sig + "\n    pass"
        else:
            code = "def _empty():\n    pass"
    return code
