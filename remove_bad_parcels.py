import pandas as pd
from glob import glob
import argparse
import os

# Remove specified rows from pconn csv files due to 0 values in these rows
# Needed for ICC calculation. Empty rows only present in fMRIprep 23.2.1 due to upgraded FSL version.

def remove_rows(path):
    csv = pd.read_csv(path)
    csv = csv.drop([16,17,176,312])
    out_csv = path.replace("sub-", "cleaned_sub-")
    csv.to_csv(out_csv, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove bad (empty) parcels from .csv pconn")
    parser.add_argument("csv_path", type=str, help="Path to the dir with .csv files to convert")

    args = parser.parse_args()

    paths = glob(os.path.join(args.csv_path, "*.csv"))

    for path in paths:
        remove_rows(path)
