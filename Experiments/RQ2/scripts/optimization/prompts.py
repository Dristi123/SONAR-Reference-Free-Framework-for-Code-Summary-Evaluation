
SYSTEM = (
    "You are an expert Python engineer specializing in performance optimization. "
    "Given a function description and its signature, write a correct Python implementation "
    "that runs as fast as possible. "
    "Output ONLY the complete function definition, no explanation."
)

USER = """\
## Description
{summary}

## Function signature
```python
{func_sig}
```

Implement this function in Python, optimizing for runtime speed. \
Choose the most efficient algorithm you can. \
Output ONLY the function definition. Include any necessary imports inside the function body."""


def build_messages(summary: str, func_sig: str) -> list:
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user",   "content": USER.format(summary=summary, func_sig=func_sig)},
    ]
