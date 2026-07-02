import gc
from pathlib import Path
from typing import Dict, List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

INSTRUCT_MODELS = {"qwen2_5_coder_32b", "OLMo-3.1-32B-Instruct"}


def load_model(model_path: Path, max_new_tokens: int = 512, load_in_4bit: bool = False):
    name = str(model_path).strip().lower()
    if name == "gemini":
        return GeminiModel()
    name = Path(model_path).name
    if name in INSTRUCT_MODELS:
        return LocalModel(model_path, max_new_tokens=max_new_tokens, load_in_4bit=load_in_4bit)
    return CompletionModel(model_path, max_new_tokens=max_new_tokens, load_in_4bit=load_in_4bit)


class GeminiModel:
    name = "gemini"

    def __init__(self):
        from gemini_client import llm_client
        self._llm_client = llm_client
        print("[model] GeminiModel ready (API)", flush=True)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_new_tokens: Optional[int] = None,
    ) -> str:
        prompt = "\n\n".join(m["content"] for m in messages)
        return self._llm_client(prompt, temperature=temperature).strip()

    def unload(self):
        pass


class LocalModel:
    def __init__(self, model_path: Path, max_new_tokens: int = 512, load_in_4bit: bool = False):
        model_path = Path(model_path)
        self.name = model_path.name

        print(f"[model] loading {model_path.name} {'(4-bit)' if load_in_4bit else ''} …", flush=True)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path, trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        major, _ = torch.cuda.get_device_capability()
        dtype = torch.bfloat16 if major >= 8 else torch.float16

        if load_in_4bit:
            from transformers import BitsAndBytesConfig
            bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=dtype)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=dtype,
                device_map="auto",
                trust_remote_code=True,
            )
        self.max_new_tokens = max_new_tokens
        print(f"[model] {model_path.name} loaded", flush=True)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_new_tokens: Optional[int] = None,
    ) -> str:
        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            prompt = (
                "\n".join(f"<{m['role']}>\n{m['content']}" for m in messages)
                + "\n<assistant>\n"
            )

        inputs = self.tokenizer(
            prompt, return_tensors="pt", truncation=True
        ).to(self.model.device)
        plen = inputs["input_ids"].shape[1]

        sample = temperature is not None and temperature > 0
        with torch.inference_mode():
            out = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens or self.max_new_tokens,
                do_sample=sample,
                temperature=temperature if sample else None,
                top_p=0.95 if sample else None,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        return self.tokenizer.decode(out[0][plen:], skip_special_tokens=True).strip()

    def unload(self):
        del self.model, self.tokenizer
        gc.collect()
        torch.cuda.empty_cache()


class CompletionModel:
    def __init__(self, model_path: Path, max_new_tokens: int = 64, load_in_4bit: bool = False):
        model_path = Path(model_path)
        self.name = model_path.name

        print(f"[model] loading {model_path.name} (completion mode) {'(4-bit)' if load_in_4bit else ''} …", flush=True)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path, trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        major, _ = torch.cuda.get_device_capability()
        dtype = torch.bfloat16 if major >= 8 else torch.float16

        if load_in_4bit:
            from transformers import BitsAndBytesConfig
            bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=dtype)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=dtype,
                device_map="auto",
                trust_remote_code=True,
            )
        self.max_new_tokens = max_new_tokens
        print(f"[model] {model_path.name} loaded", flush=True)

    def complete(self, prompt: str, max_new_tokens: Optional[int] = None) -> str:
        inputs = self.tokenizer(
            prompt, return_tensors="pt", truncation=True
        ).to(self.model.device)
        plen = inputs["input_ids"].shape[1]

        with torch.inference_mode():
            out = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens or self.max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        return self.tokenizer.decode(out[0][plen:], skip_special_tokens=True).strip()

    def unload(self):
        del self.model, self.tokenizer
        gc.collect()
        torch.cuda.empty_cache()
