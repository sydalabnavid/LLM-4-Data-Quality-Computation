#!/usr/bin/env python3
import argparse
import pandas as pd
import numpy as np
import sys

def count_inconsistent_numeric(series):
    """
    Count entries not convertible to numeric (excluding original missing).
    """
    non_missing = series.notna()
    coerced = pd.to_numeric(series, errors='coerce')
    invalid = coerced.isna() & non_missing
    return int(invalid.sum())

def count_inconsistent_datetime(series):
    """
    Count entries not convertible to datetime (excluding original missing).
    """
    non_missing = series.notna()
    coerced = pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
    invalid = coerced.isna() & non_missing
    return int(invalid.sum())

def main():
    parser = argparse.ArgumentParser(
        description='Check consistency in data formats (numeric/datetime).')
    parser.add_argument('file', help='Path to input CSV or Excel file')
    args = parser.parse_args()

    # Read file
    try:
        if args.file.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(args.file)
        else:
            df = pd.read_csv(args.file, sep=None, engine='python')
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    total_rows = len(df)
    cols = df.columns.tolist()

    # Summary per column
    summary = []
    overall_inconsistent = 0
    for col in cols:
        series = df[col]
        non_missing_count = series.notna().sum()
        if pd.api.types.is_numeric_dtype(series):
            # Numeric consistency
            inc_count = count_inconsistent_numeric(series)
            dtype = 'numeric'
        else:
            # Try datetime consistency
            inc_dt = count_inconsistent_datetime(series)
            if series.notna().sum() > 0 and inc_dt < non_missing_count:
                inc_count = inc_dt
                dtype = 'datetime'
            else:
                # Other types: assume consistent
                inc_count = 0
                dtype = 'other'
        consistency_pct = ((total_rows - inc_count) / total_rows) * 100 if total_rows > 0 else 0.0
        summary.append((col, dtype, inc_count, consistency_pct))
        overall_inconsistent += inc_count

    # Overall consistency across all cells
    total_cells = total_rows * len(cols)
    overall_consistency = ((total_cells - overall_inconsistent) / total_cells) * 100 if total_cells > 0 else 0.0

    # Print results
    print("\nConsistency Summary per column:\n")
    print(f"{'Column':20s}{'Type':10s}{'Inconsistent':>15s}{'Consistency(%)':>15s}")
    for col, dtype, inc, pct in summary:
        print(f"{col:20s}{dtype:10s}{inc:15d}{pct:15.2f}")

    print("\nOverall consistency across all cells:\n")
    print(f"Total cells      : {total_cells}")
    print(f"Inconsistent cells: {overall_inconsistent}")
    print(f"Consistency (%): {overall_consistency:.2f}")

if __name__ == '__main__':
    main()
