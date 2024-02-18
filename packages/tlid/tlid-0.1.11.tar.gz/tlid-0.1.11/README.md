# tlid

## Installation

```sh
pip install tlid
```

## Usage:
```python

import tlid

# Get TLID
tlid_str = tlid.get_tlid()
print(tlid_str)  # Outputs: YYMMDDHHMMSS

# Get TLID with milliseconds
tlid_milli = tlid.get_milliseconds()
print(tlid_milli)  # Outputs: YYMMDDHHMMSSmmm

# Get TLID for different time granularities
print(tlid.get_seconds())  # Outputs: YYMMDDHHMMSS
print(tlid.get_minutes())  # Outputs: YYMMDDHHMM
print(tlid.get_hour())     # Outputs: YYMMDDHH
print(tlid.get_day())      # Outputs: YYMMDD
print(tlid.get_month())    # Outputs: YYMM
print(tlid.get_year())     # Outputs: YY

# Check if a string has a TLID
print(tlid.has_tlid('Hello 210101010101 World'))  # Outputs: True

# Extract TLID from a string
print(tlid.extract_tlid('Hello 210101010101 World'))  # Outputs: 210101010101

# Clean a string from its TLID
print(tlid.clean_tlid('Hello 210101010101 World'))  # Outputs: Hello World

# Convert a TLID string to a datetime object
print(tlid.to_date('210101010101'))  # Outputs: 2021-01-01 01:01:01

```



```markdown
# pytlid

`pytlid` is a command-line interface for generating time-based identifiers using the `tlid` Python package.



## Usage

To use `pytlid`, simply run the command followed by the desired time unit. The default time unit is minutes if no argument is provided.

```sh
pytlid [unit]
```

Here are the available units and their corresponding outputs:

- `h`: Current hour in YYMMDDHH format
- `s`: Current seconds in YYMMDDHHMMSS format
- `ms`: Current milliseconds in YYMMDDHHMMSSmmm format
- `m`: Current month in YYMM format
- `M`: Current month in YYMM format (same as `m`)
- `y`: Current year in YY format
- `d`: Current day in YYMMDD format

### Examples

To get the current time in minutes:

```sh
pytlid
```

To get the current time in hours:

```sh
pytlid h
```

To get the current time in seconds:

```sh
pytlid s
```

For help:

```sh
pytlid --help
```

This will display the help message for the `pytlid` command.
```

