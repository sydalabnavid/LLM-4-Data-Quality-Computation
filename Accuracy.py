#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
import sys

def count_outliers(series, z_thresh):
    """
    Count number of outliers in a pandas Series using z-score.
    Non-numeric or constant-series produce zero outliers.
    """
    try:
        arr = series.dropna().astype(float).values
    except:
        return 0
    if arr.size == 0:
        return 0
    mean = arr.mean()
    std = arr.std(ddof=0)
    if std == 0:
        return 0
    z_scores = np.abs((arr - mean) / std)
    return int((z_scores > z_thresh).sum())

def main():
    parser = argparse.ArgumentParser(
        description='Compute missing, outliers, drift=0, correctness and accuracy per column and overall.')
    parser.add_argument('file', help='Path to CSV or Excel file')
    parser.add_argument('--z_thresh', type=float, default=3.0,
                        help='Z-score threshold for outlier detection (default: 3.0)')
    args = parser.parse_args()

    # Load file
    try:
        if args.file.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(args.file)
        else:
            df = pd.read_csv(args.file, sep=None, engine='python')
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    total_rows = len(df)
    columns = df.columns.tolist()

    # Summary per column
    summary = []
    for col in columns:
        missing = int(df[col].isna().sum())
        outliers = count_outliers(df[col], args.z_thresh)
        drift_fail = 0  # no baseline provided
        correct = total_rows - missing - outliers - drift_fail
        accuracy = (correct / total_rows) * 100 if total_rows > 0 else 0.0
        summary.append((col, missing, outliers, drift_fail, correct, accuracy))

    # Print column summary
    print("\nAccuracy Summary per column:\n")
    print(f"{'Column':20s}{'Missing':>10s}{'Outliers':>10s}{'DriftFail':>10s}{'Correct':>10s}{'Accuracy(%)':>12s}")
    for col, miss, out, drift, corr, acc in summary:
        print(f"{col:20s}{miss:10d}{out:10d}{drift:10d}{corr:10d}{acc:12.2f}")

    # Overall summary
    n_cols = len(columns)
    total_cells = total_rows * n_cols
    missing_cells = sum(x[1] for x in summary)
    outlier_cells = sum(x[2] for x in summary)
    drift_cells = 0
    correct_cells = total_cells - missing_cells - outlier_cells - drift_cells
    overall_accuracy = (correct_cells / total_cells) * 100 if total_cells > 0 else 0.0

    print("\nOverall summary:\n")
    print(f"Total cells    : {total_cells}")
    print(f"Missing cells  : {missing_cells}")
    print(f"Outlier cells  : {outlier_cells}")
    print(f"Drift-fail cells: {drift_cells}")
    print(f"Correct cells  : {correct_cells}")
    print(f"Overall Accuracy (%): {overall_accuracy:.2f}")

if __name__ == '__main__':
    main()
