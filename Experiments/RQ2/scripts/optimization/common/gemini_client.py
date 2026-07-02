#!/usr/bin/env python3

import os
import time
import google.genai as genai
from google.genai import types

PROJECT  = os.environ["GEMINI_VERTEX_PROJECT"]
LOCATION = os.environ["GEMINI_VERTEX_LOCATION"]
MODEL    = "gemini-2.5-flash"

_client = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=PROJECT,
            location=LOCATION,
        )
    return _client


def llm_client(prompt: str, retries: int = 5, call_timeout: int = 120,
               temperature: float | None = None) -> str:
    import concurrent.futures
    client = _get_client()
    delay = 30
    config = types.GenerateContentConfig(temperature=temperature) if temperature is not None else None
    for attempt in range(retries):
        try:
            ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            fut = ex.submit(
                client.models.generate_content, model=MODEL, contents=prompt, config=config
            )
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
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < retries - 1:
                    print(f"[gemini] rate limited, retrying in {delay}s...", flush=True)
                    time.sleep(delay)
                    delay = min(delay * 2, 300)
                else:
                    raise
            else:
                raise
