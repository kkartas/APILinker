from __future__ import annotations

import argparse
from pathlib import Path

from .benchmark_harness import run_scenarios
from .scenarios import SCENARIOS


def main():
    parser = argparse.ArgumentParser(description="Run ApiLinker benchmark scenarios")
    parser.add_argument("--iterations", type=int, default=10, help="Iterations per scenario")
    parser.add_argument("--out", type=str, default=str(Path("benchmarks") / "results"))
    args = parser.parse_args()

    out_dir = Path(args.out)
    results = run_scenarios(SCENARIOS, iterations=args.iterations, out_dir=out_dir)
    print(f"Wrote results to {out_dir}")


if __name__ == "__main__":
    main()


