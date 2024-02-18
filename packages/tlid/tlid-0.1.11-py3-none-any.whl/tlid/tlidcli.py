#!/usr/bin/env python
# tlidcli.py

import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
#import tlid
#from . import tlid

from . import (
    get_minutes,
    get_hour,
    get_seconds,
    get_milliseconds,
    get_month,
    get_year,
    get_day,
    strdt,
)


def main():
    # Create the parser
    parser = argparse.ArgumentParser(
        description="TLID CLI - Generate time-based identifiers."
    )

    # Add arguments
    parser.add_argument(
        "unit",
        nargs="?",
        default="minutes",
        choices=["h", "s", "ms", "m", "M", "y", "d", "minutes","dt"],
        help="Select the unit of time for TLID generation (default: minutes).",
    )
    # Add nextarg argument
    parser.add_argument(
        "nextarg",
        nargs="?",
        default="",
        help="The next argument.",
    )

    # Parse the arguments
    args = parser.parse_args()

    # Get the TLID based on the selected unit
    if args.unit in ["h", "s", "ms", "m", "M", "y", "d", "minutes"]:
        
        if args.unit == "h" or args.unit == "H" or args.unit == "hour":
            print(get_hour())
        elif args.unit == "s" or args.unit == "S" or args.unit == "seconds":
            print(get_seconds())
        elif args.unit == "ms" or args.unit == "MS" or args.unit == "milliseconds":
            print(get_milliseconds())
        elif args.unit == "m" or args.unit == "month":
            print(get_month())
        elif args.unit == "y" or args.unit == "Y" or args.unit == "year":
            print(get_year())
        elif args.unit == "d" or args.unit == "D" or args.unit == "day":
            print(get_day())
        elif args.unit == "minutes" or args.unit == "min" or args.unit == "MINUTES":
            print(get_minutes())
    else:  
        print(strdt(args.nextarg))


# This is the standard boilerplate that calls the main() function.
if __name__ == "__main__":
    main()
