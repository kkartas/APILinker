from __future__ import annotations

import argparse
import os
from pathlib import Path

from .benchmark_harness import run_scenarios
from .scenarios import SCENARIOS


def main():
    parser = argparse.ArgumentParser(description="Run ApiLinker benchmark scenarios")
    parser.add_argument("--iterations", type=int, default=10, help="Iterations per scenario")
    parser.add_argument("--out", type=str, default=str(Path("benchmarks") / "results"))
    parser.add_argument("--async-concurrency", type=int, help="Override async concurrency for benchmarks")
    parser.add_argument("--async-batch", type=int, help="Override async batch size for benchmarks")
    args = parser.parse_args()

    out_dir = Path(args.out)
    # Propagate async tuning options via environment for scenarios
    if args.async_concurrency:
        os.environ["APILINKER_ASYNC_CONCURRENCY"] = str(args.async_concurrency)
    if args.async_batch:
        os.environ["APILINKER_ASYNC_BATCH"] = str(args.async_batch)
    results = run_scenarios(SCENARIOS, iterations=args.iterations, out_dir=out_dir)
    print(f"Wrote results to {out_dir}")


if __name__ == "__main__":
    main()


