import argparse
from pathlib import Path
import pandas as pd

from .read import read_onelist_dataframe


def yaml2csv(inpath, outpath=None, encoding='utf-8'):
    inpath = Path(inpath)
    suffix = inpath.suffix
    if outpath:
        outpath = Path(outpath)
    else:
        outpath = inpath.with_suffix('.yaml')

    with open(inpath, 'r') as f:
        df = read_onelist_dataframe(f)
    df.to_csv(outpath, encoding=encoding, index=False)
    print("Done writing CSV file: {}".format(outpath.name))


def parse_arguments():
    parser = argparse.ArgumentParser(description='Read CSV file using Pandas read_csv() function.')

    parser.add_argument('file_path', type=str, help='Path to the CSV file')


    # Optional arguments
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Character indicating the start of a comment line in the CSV file')
    parser.add_argument('-e', '--encoding', type=str, default='utf-8',
                        help='Character indicating the start of a comment line in the CSV file')

    return parser.parse_args()

def main():
    # Check if the script is being run as the main program
    # Parse command line arguments
    args = parse_arguments()

    # Read CSV file using Pandas read_csv() function
    try:
        yaml2csv(args.file_path, args.output, args.encoding)
    except FileNotFoundError:
        print(f"Error: File not found at {args.file_path}")
    except pd.errors.EmptyDataError:
        print(f"Error: The CSV file at {args.file_path} is empty")


# Run the main function
if __name__ == "__main__":
    main()
