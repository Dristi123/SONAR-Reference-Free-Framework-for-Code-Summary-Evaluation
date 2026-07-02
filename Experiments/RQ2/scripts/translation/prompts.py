import re

SYSTEM = (
    "You are an expert Java developer. "
    "You will be given a function description and a Java class skeleton ending at the "
    "opening brace of the method. "
    "Write ONLY the method body — the lines that go inside the opening { of the method. "
    "Do NOT repeat the method signature, class declaration, imports, or any closing braces."
)

USER = """\
## Description
{description}

## Java class to complete (write the body of the method below):
```java
{skeleton}
```

Output only the method body lines (what goes between the opening {{ and the closing }})."""


def get_java_skeleton(prompt: str) -> str:
    lines = prompt.splitlines(keepends=True)
    out = []
    in_comment_block = False
    sig_written = False
    for line in lines:
        stripped = line.strip()
       
        if sig_written:
            break
                                                        
        if in_comment_block and stripped.startswith("//"):
            continue
                                                                           
        if in_comment_block and not stripped.startswith("//"):
            in_comment_block = False
        if stripped == "class Problem {":
            in_comment_block = True
            out.append(line)
            continue
                                                       
        if stripped.startswith("public static"):
            out.append(line)
            sig_written = True
            continue
        out.append(line)
    return "".join(out).rstrip()


def build_messages(description: str, skeleton: str) -> list:
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user",   "content": USER.format(
            description=description,
            skeleton=skeleton,
        )},
    ]


def extract_body(raw: str) -> str:
                           
    text = re.sub(r"```[a-zA-Z]*\s*\n?", "", raw)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

                                                                                     
    if re.search(r"\bclass\s+Problem\b", text) or re.search(r"\bpublic\s+static\b", text):
        m = re.search(r"public\s+static\b.*?\{", text, re.DOTALL)
        if m:
            text = text[m.end():].strip()
                                                                                      
            text = re.sub(r"\s*\}\s*\}\s*$", "", text).strip()
            text = re.sub(r"\s*\}\s*$", "", text).strip()

    return text
