import json
import subprocess
import argparse
import sys
import pandas as pd
from pandas.errors import EmptyDataError

from .datagenerators.generate_data import generate_data

from .panel.main_panel import render_panel


class Arguments:
    def __init__(self, csvFile, jsonFile) -> None:
        if ".csv" not in csvFile.name.lower():
            raise TypeError("CSV file not passed to data.")
        if ".json" not in jsonFile.name.lower():
            raise TypeError("JSON file not passed to options.")

        with jsonFile:
            try:
                self.options = json.load(jsonFile)
                print("Options loaded...")
            except:
                raise TypeError("Invalid JSON format in options file.")
        with csvFile:
            try:
                # TODO: load csv file
                self.data = pd.read_csv(csvFile)
                self.data_file_name = csvFile.name
                print("Data loaded...")
            except EmptyDataError as ed:
                raise EmptyDataError(ed)
            except:
                raise TypeError(
                    "Error reading data. Make sure it can be read with pd.read_csv(csvFile)."
                )


def main(argv=None):
    """argv is an array of strings, simulating command line arguments"""
    parser = argparse.ArgumentParser(
        description="Command-Line Interface for GeoViz Project"
    )
    # https://docs.python.org/3/library/argparse.html#action
    parser.add_argument(
        "data",
        metavar="csvfilepath",
        help="File path to CSV file to be analyzed",
        type=argparse.FileType("r", encoding="UTF-8"),
    )
    parser.add_argument(
        "--options",
        help="File path to the JSON configuration folder",
        metavar="jsonfilepath",
        type=argparse.FileType("r", encoding="UTF-8"),
    )
    parser.add_argument(
        "--test",
        help="Disables starting Panel server for testing",
        action=argparse.BooleanOptionalAction,
    )
    args = parser.parse_args(argv)
    arguments = Arguments(args.data, args.options)

    if args.test:
        print("Testing mode enabled")
    data_dict = generate_data(arguments=arguments)
    filled_template = render_panel(args=arguments, data_dict=data_dict, test=args.test)
    return filled_template


if __name__ == "__main__":
    sys.exit(main())
