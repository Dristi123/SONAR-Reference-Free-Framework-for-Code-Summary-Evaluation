import re
import signal
import types
from typing import List, Optional

try:
    from cirron import Collector
    _CIRRON_AVAILABLE = True
except ImportError:
    _CIRRON_AVAILABLE = False


_INF = float("inf")
_N_RUNS = 5


def _parse_input(input_str: str):
    return eval(input_str)                                                        


def _run_once(fn, args) -> int:
    if not _CIRRON_AVAILABLE:
        raise RuntimeError("cirron not installed — pip install cirron")
    try:
        with Collector() as col:
            if isinstance(args, (tuple, list)):
                fn(*args)
            else:
                fn(args)
        return col.counters.instruction_count
    except TimeoutError:
        raise
    except Exception:
        return _INF


def _load_fn(code: str, entry_point: str):
    ns = {}
    exec(compile(code, "<coffe>", "exec"), ns)              
    return ns[entry_point]


def measure_instructions(
    code: str,
    entry_point: str,
    stress_inputs: List[str],
    timeout: int = 30,
) -> List[float]:
    try:
        fn = _load_fn(code, entry_point)
    except Exception:
        return [_INF] * len(stress_inputs)

    def _sigalrm(signum, frame):
        raise TimeoutError()

    results = []
    for inp_str in stress_inputs:
        try:
            args = _parse_input(inp_str)
        except Exception:
            results.append(_INF)
            continue

        signal.signal(signal.SIGALRM, _sigalrm)
        signal.alarm(timeout)
        try:
            counts = []
            for _ in range(_N_RUNS):
                c = _run_once(fn, args)
                counts.append(c)
        except TimeoutError:
            results.append(_INF)
            continue
        finally:
            signal.alarm(0)

        if _INF in counts:
            results.append(_INF)
        else:
            counts.remove(max(counts))
            counts.remove(min(counts))
            results.append(sum(counts) / len(counts))

    return results


def compare_efficiency(
    canonical_code: str,
    generated_code: str,
    entry_point: str,
    stress_inputs: List[str],
    timeout: int = 30,
) -> dict:
    can_counts = measure_instructions(canonical_code, entry_point, stress_inputs, timeout)
    gen_counts = measure_instructions(generated_code, entry_point, stress_inputs, timeout)

    ratios = []
    for c, g in zip(can_counts, gen_counts):
        if c != _INF and g != _INF and g > 0:
            ratios.append(c / g)

    return {
        "canonical_counts": can_counts,
        "generated_counts": gen_counts,
        "speedup_ratios":   ratios,
        "mean_speedup":     sum(ratios) / len(ratios) if ratios else None,
        "valid":            len(ratios),
    }
