import pandas as pd
import argparse
from pathlib import Path

from .write import write_dataframe


def df2yaml(df, inpath, outpath=None):
    inpath = Path(inpath)
    suffix = inpath.suffix
    if outpath:
        outpath = Path(outpath)
    else:
        outpath = inpath.with_suffix('.yaml')

    write_dataframe(outpath, df, name='data')
    print("Done writing YAML file: {}".format(outpath.name))


def parse_arguments():
    parser = argparse.ArgumentParser(description='Read CSV file using Pandas read_csv() function.')

    parser.add_argument('file_path', type=str, help='Path to the CSV file')


    # Optional arguments
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Character indicating the start of a comment line in the CSV file')
    parser.add_argument('-s', '--separator', type=str, default=',',
                        help='Separator used in the CSV file (default is comma)')

    parser.add_argument('-c', '--columns', default=None, nargs='+',
                        help='List of columns to select from the CSV file')

    parser.add_argument('-H', '--header', default='infer', action='store_true',
                        help='Specify if the CSV file has a header row')

    parser.add_argument('--comment', type=str, default=None,
                        help='Character indicating the start of a comment line in the CSV file')

    return parser.parse_args()

def main():
    # Check if the script is being run as the main program
    # Parse command line arguments
    args = parse_arguments()

    # Read CSV file using Pandas read_csv() function
    try:
        df = pd.read_csv(args.file_path, sep=args.separator, header=0 if args.header else None,
                         usecols=args.columns, comment=args.comment)
        df2yaml(df, args.file_path, args.output)
    except FileNotFoundError:
        print(f"Error: File not found at {args.file_path}")
    except pd.errors.EmptyDataError:
        print(f"Error: The CSV file at {args.file_path} is empty")


# Run the main function
if __name__ == "__main__":
    main()
