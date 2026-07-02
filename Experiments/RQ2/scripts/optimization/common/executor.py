import re
import signal
from typing import Dict, List


class _Timeout(Exception):
    pass

def _alarm(signum, frame):
    raise _Timeout()


def run_assert(assert_stmt: str, func_code: str, timeout: int = 5) -> str:
    script = func_code + "\n" + assert_stmt
    ns: Dict = {}
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(timeout)
    try:
        exec(compile(script, "<assert>", "exec"), ns)
        return "pass"
    except AssertionError:
        return "fail"
    except _Timeout:
        return "timeout"
    except Exception as e:
        return f"error:{type(e).__name__}"
    finally:
        signal.alarm(0)


def run_test_suite(asserts: List[str], func_code: str, timeout: int = 5) -> Dict:
    if not asserts:
        return {
            "passed": 0, "failed": 0, "errored": 0,
            "total": 0, "pass_rate": 0.0, "results": [],
        }

    results = [run_assert(a, func_code, timeout) for a in asserts]
    passed  = sum(1 for r in results if r == "pass")
    failed  = sum(1 for r in results if r == "fail")
    errored = len(results) - passed - failed

    return {
        "passed":   passed,
        "failed":   failed,
        "errored":  errored,
        "total":    len(results),
        "pass_rate": passed / len(results),
        "results":  results,
    }


def parse_asserts(raw: str) -> List[str]:
    asserts = []
    in_fence = False
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if stripped.startswith("assert "):
            asserts.append(stripped)
    return asserts


def extract_code(raw: str, func_sig: str = "") -> str:
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
        return (func_sig + "\n    pass") if func_sig else "def _empty():\n    pass"
    return code
