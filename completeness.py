#python3
# pip3 install pandas openpyxl
# For a CSV file
# python3 completeness.py data/my_dataset.csv

# # Or, if you made it executable:
# ./completeness.py data/my_dataset.csv

# # For an Excel file
# python3 completeness.py data/my_dataset.xlsx



#!/usr/bin/env python3
import argparse
import pandas as pd
import sys

def calculate_completeness(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate completeness for each column and the entire dataset.
    """
    # Replace empty strings or whitespace-only strings with NaN
    df = df.replace(r'^\s*$', pd.NA, regex=True)

    # Completeness per column
    col_completeness = df.notna().mean() * 100
    col_completeness.name = 'completeness_%'

    # Overall dataset completeness
    total_cells = df.size
    non_null_cells = df.notna().sum().sum()
    overall_completeness = (non_null_cells / total_cells) * 100

    # Combine results into a DataFrame
    completeness_summary = col_completeness.to_frame()
    completeness_summary.loc['Overall'] = overall_completeness

    return completeness_summary

def main():
    parser = argparse.ArgumentParser(
        description='Calculate completeness of each column and the overall dataset.')
    parser.add_argument('file', help='Path to input CSV or Excel file')
    args = parser.parse_args()

    # Read input file with delimiter sniffing
    try:
        if args.file.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(args.file)
        else:
            # auto-detect delimiter (comma, semicolon, etc.)
            df = pd.read_csv(args.file, sep=None, engine='python')
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    summary = calculate_completeness(df)
    print("\nCompleteness Summary:\n")
    print(summary.to_string())

if __name__ == '__main__':
    main()




# resaults example 
# Completeness Summary:

#              completeness_%
# column_a              98.5
# column_b              76.2
# column_c             100.0
# Overall               91.6
