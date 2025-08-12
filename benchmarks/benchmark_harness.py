"""
Benchmark harness for ApiLinker.

Provides utilities to run repeatable benchmarks and collect metrics
without external dependencies.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import tracemalloc
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class RunStats:
    iterations: int
    duration_seconds: float
    mean_ms: float
    median_ms: float
    p95_ms: float
    min_ms: float
    max_ms: float
    rps: float
    peak_memory_mb: float
    metadata: Dict[str, Any]


def time_function(func: Callable[[], Any], iterations: int = 10, warmup: int = 3) -> RunStats:
    """Time a callable over multiple iterations with warmup and memory profiling."""
    # Warmup
    for _ in range(warmup):
        func()

    durations: List[float] = []

    tracemalloc.start()
    start_all = time.perf_counter()
    for _ in range(iterations):
        t0 = time.perf_counter()
        func()
        t1 = time.perf_counter()
        durations.append((t1 - t0) * 1000.0)  # ms
    end_all = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    duration_seconds = end_all - start_all
    mean_ms = statistics.mean(durations)
    median_ms = statistics.median(durations)
    p95_ms = sorted(durations)[int(0.95 * len(durations)) - 1]
    min_ms = min(durations)
    max_ms = max(durations)
    rps = iterations / duration_seconds if duration_seconds > 0 else float("inf")

    return RunStats(
        iterations=iterations,
        duration_seconds=duration_seconds,
        mean_ms=mean_ms,
        median_ms=median_ms,
        p95_ms=p95_ms,
        min_ms=min_ms,
        max_ms=max_ms,
        rps=rps,
        peak_memory_mb=peak / (1024 * 1024),
        metadata={},
    )


def save_results(results: Dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    # JSON
    json_path = out_dir / "results.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Markdown summary
    md = [
        "# ApiLinker Benchmarks",
        "",
        f"Total scenarios: {len(results)}",
        "",
    ]
    for name, data in results.items():
        stats = data.get("stats", {})
        md.extend(
            [
                f"## {name}",
                "",
                f"- iterations: {stats.get('iterations')}",
                f"- duration_seconds: {stats.get('duration_seconds'):.4f}",
                f"- mean_ms: {stats.get('mean_ms'):.2f}",
                f"- median_ms: {stats.get('median_ms'):.2f}",
                f"- p95_ms: {stats.get('p95_ms'):.2f}",
                f"- min_ms: {stats.get('min_ms'):.2f}",
                f"- max_ms: {stats.get('max_ms'):.2f}",
                f"- rps: {stats.get('rps'):.2f}",
                f"- peak_memory_mb: {stats.get('peak_memory_mb'):.2f}",
                "",
            ]
        )
    (out_dir / "README.md").write_text("\n".join(md), encoding="utf-8")


def run_scenarios(scenarios: Dict[str, Callable[[], Any]], iterations: int, out_dir: Path) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for name, scenario_func in scenarios.items():
        stats = time_function(lambda: scenario_func(), iterations=iterations)
        results[name] = {"stats": asdict(stats)}
    save_results(results, out_dir)
    return results


def main():
    parser = argparse.ArgumentParser(description="Run ApiLinker benchmarks")
    parser.add_argument("--iterations", type=int, default=20, help="Iterations per scenario")
    parser.add_argument(
        "--out", type=str, default=str(Path("benchmarks") / "results"), help="Output directory"
    )
    args = parser.parse_args()

    # Scenarios are provided by benchmarks/scenarios.py when used via run_benchmarks.py
    print("Use benchmarks/run_benchmarks.py to execute scenarios.")


if __name__ == "__main__":
    main()


