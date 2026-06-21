#!/usr/bin/env python3
"""
check_status.py - Summarize experiment completion across a results directory tree.

Usage:
    python tools/check_status.py <results_dir> [--save-failed <path>]

Exit codes:
    0  All experiments complete
    1  Some experiments pending or failed
"""
import argparse
import os
import sys


def classify_leaf(dirpath):
    """Return 'DONE', 'FAILED', or 'PENDING' for a leaf experiment directory."""
    has_pickle = os.path.isfile(os.path.join(dirpath, "fi.pickle"))
    has_stats = os.path.isfile(os.path.join(dirpath, "fi.stats"))

    if has_pickle and has_stats:
        return "DONE"
    if has_pickle or has_stats:
        return "FAILED"
    return "PENDING"


def is_leaf(dirpath):
    """A leaf directory contains an encoder.json config (written by generate_fi_jobs)."""
    return os.path.isfile(os.path.join(dirpath, "encoder.json"))


def walk_results(root):
    """Yield (dirpath, status) for every leaf experiment directory under root."""
    for dirpath, dirnames, _ in os.walk(root):
        dirnames.sort()
        if is_leaf(dirpath):
            dirnames.clear()
            yield dirpath, classify_leaf(dirpath)


def main():
    parser = argparse.ArgumentParser(
        description="Summarize fault-injection experiment completion."
    )
    parser.add_argument("results_dir", help="Root directory of the experiment tree")
    parser.add_argument(
        "--save-failed",
        metavar="PATH",
        default=None,
        help="Write paths of FAILED and PENDING experiments to this file",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print status for every experiment (not just the summary)",
    )
    args = parser.parse_args()

    results_dir = os.path.abspath(args.results_dir)
    if not os.path.isdir(results_dir):
        print(f"Error: '{results_dir}' is not a directory.", file=sys.stderr)
        sys.exit(2)

    counts = {"DONE": 0, "FAILED": 0, "PENDING": 0}
    incomplete = []

    for dirpath, status in walk_results(results_dir):
        counts[status] += 1
        if status != "DONE":
            incomplete.append((dirpath, status))
        if args.verbose:
            rel = os.path.relpath(dirpath, results_dir)
            print(f"  [{status:7s}]  {rel}")

    total = sum(counts.values())
    print(f"\nResults under: {results_dir}")
    print(f"  Total experiments : {total}")
    print(f"  DONE              : {counts['DONE']}")
    print(f"  PENDING           : {counts['PENDING']}")
    print(f"  FAILED            : {counts['FAILED']}")

    if args.save_failed and incomplete:
        with open(args.save_failed, "w") as f:
            for dirpath, status in incomplete:
                f.write(f"{status}\t{dirpath}\n")
        print(f"\nIncomplete experiments written to: {args.save_failed}")

    if incomplete:
        print(
            f"\n{len(incomplete)} experiment(s) are not complete. "
            "Re-submit with generate_fi_jobs.py or check HPC queue."
        )
        sys.exit(1)

    print("\nAll experiments complete.")
    sys.exit(0)


if __name__ == "__main__":
    main()
