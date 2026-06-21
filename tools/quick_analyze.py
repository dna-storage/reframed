#!/usr/bin/env python3
"""
quick_analyze.py - Print a summary of fault-injection results from a results directory.

Usage:
    python tools/quick_analyze.py <results_dir> [options]

Examples:
    python tools/quick_analyze.py results/ --group error_rate
    python tools/quick_analyze.py results/ --group error_rate coverage --save summary.csv
    python tools/quick_analyze.py results/ --group encoder::encoder error_rate
"""
import argparse
import os
import sys

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install with: pip install pandas", file=sys.stderr)
    sys.exit(1)


def find_db_gen():
    """Return the path to db_gen.py relative to this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "data_analysis", "db_gen.py")


def load_dataframe(results_dir, db_name="__quick_analyze_tmp"):
    """Build a DataFrame from results_dir using db_gen logic directly."""
    db_gen_path = find_db_gen()
    if not os.path.isfile(db_gen_path):
        print(f"Error: db_gen.py not found at {db_gen_path}", file=sys.stderr)
        sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("db_gen", db_gen_path)
    db_gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(db_gen)

    paths = db_gen.find_data_paths(results_dir)
    if not paths:
        print(f"No completed experiments found under '{results_dir}'.", file=sys.stderr)
        sys.exit(1)

    rows = []
    for p in paths:
        try:
            row = db_gen.load_fi_json(p)
            rows.append(row)
        except Exception as e:
            print(f"Warning: could not load {p}: {e}", file=sys.stderr)

    if not rows:
        print("No data could be loaded.", file=sys.stderr)
        sys.exit(1)

    return pd.DataFrame(rows)


def compute_metrics(df):
    """Add derived metric columns if the raw columns exist."""
    if "total_mismatch_bytes" in df.columns and "file_size_bytes" in df.columns:
        mask = df["file_size_bytes"] > 0
        df["byte_error_rate"] = 0.0
        df.loc[mask, "byte_error_rate"] = (
            df.loc[mask, "total_mismatch_bytes"] / df.loc[mask, "file_size_bytes"]
        )
        df["ber"] = df["byte_error_rate"] * 8
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Summarize fault-injection experiment results."
    )
    parser.add_argument("results_dir", help="Root directory of experiment results")
    parser.add_argument(
        "--group",
        nargs="+",
        default=["error_rate"],
        metavar="COL",
        help="Columns to group by (default: error_rate). Use 'encoder::encoder' for prefixed columns.",
    )
    parser.add_argument(
        "--metrics",
        nargs="+",
        default=["ber", "byte_error_rate", "error", "total_strands_analyzed"],
        metavar="COL",
        help="Metric columns to summarize (default: ber byte_error_rate error total_strands_analyzed)",
    )
    parser.add_argument(
        "--save",
        metavar="PATH",
        default=None,
        help="Save the summary table to a CSV file",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Print the raw DataFrame instead of the grouped summary",
    )
    args = parser.parse_args()

    results_dir = os.path.abspath(args.results_dir)
    if not os.path.isdir(results_dir):
        print(f"Error: '{results_dir}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading results from: {results_dir}")
    df = load_dataframe(results_dir)
    df = compute_metrics(df)

    print(f"Loaded {len(df)} experiments.")

    if args.full:
        with pd.option_context("display.max_rows", None, "display.max_columns", None):
            print(df.to_string())
        if args.save:
            df.to_csv(args.save, index=False)
            print(f"\nSaved to: {args.save}")
        return

    group_cols = [c for c in args.group if c in df.columns]
    missing_group = [c for c in args.group if c not in df.columns]
    if missing_group:
        print(f"Warning: group columns not found in data: {missing_group}", file=sys.stderr)
    if not group_cols:
        print("Error: none of the requested group columns exist in the data.", file=sys.stderr)
        print(f"Available columns: {list(df.columns)}", file=sys.stderr)
        sys.exit(1)

    metric_cols = [c for c in args.metrics if c in df.columns]
    missing_metrics = [c for c in args.metrics if c not in df.columns]
    if missing_metrics:
        print(f"Note: metric columns not found (will be skipped): {missing_metrics}", file=sys.stderr)

    if not metric_cols:
        print("No metric columns available. Printing group counts only.")
        summary = df.groupby(group_cols).size().rename("count").reset_index()
    else:
        agg = {col: ["mean", "std", "count"] for col in metric_cols}
        summary = df.groupby(group_cols).agg(agg)
        summary.columns = ["_".join(c) for c in summary.columns]
        summary = summary.reset_index()

    with pd.option_context(
        "display.max_rows", None,
        "display.max_columns", None,
        "display.width", 120,
        "display.float_format", "{:.4g}".format,
    ):
        print(f"\nSummary grouped by: {group_cols}\n")
        print(summary.to_string(index=False))

    if args.save:
        summary.to_csv(args.save, index=False)
        print(f"\nSaved summary to: {args.save}")


if __name__ == "__main__":
    main()
