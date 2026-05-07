import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="Clean a CSV file")

parser.add_argument("--input", required=True, help="Input CSV file path")
parser.add_argument("--output", default="cleaned.csv", help="Output CSV file path")
parser.add_argument("--drop-missing", action="store_true", help="Drop rows with missing values")

args = parser.parse_args()

df = pd.read_csv(args.input)

if args.drop_missing:
    df = df.dropna()

df.to_csv(args.output, index=False)

print("Cleaning completed!")
print("Saved to:", args.output)