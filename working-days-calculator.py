import sys

import pandas as pd


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: {} <csv_file>".format(sys.argv[0]))
        print(
            "Go to https://numtide.harvestapp.com/reports?kind=year and export the CSV for the year"
        )
        sys.exit(1)

    csv_file = sys.argv[1]
    df = pd.read_csv(csv_file, parse_dates=["Date"])
    working_days = len(df["Date"].unique())
    start = df["Date"].min()
    end = df["Date"].max()
    print("Working days: {} from {} to {}".format(working_days, start, end))


if __name__ == "__main__":
    main()
