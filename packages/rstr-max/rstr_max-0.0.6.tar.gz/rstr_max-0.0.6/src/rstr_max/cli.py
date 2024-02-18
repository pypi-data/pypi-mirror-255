from argparse import ArgumentParser
from sys import stdout, stderr
import json

from .main import max_repeated_substrings as rstr_max
from .__about__ import __version__

parser = ArgumentParser(description="Find the maximum repeated substrings in a string or list of strings")
parser.add_argument("-i", "--input", help="The input string or list of strings (txt or json file)", required=True)
parser.add_argument("-o", "--output", help="The output file (json)", required=True)
parser.add_argument("-M", "--min_len", help="The minimum length of the substring", type=int, default=1)
parser.add_argument("-X", "--max_len", help="The maximum length of the substring", type=int, default=None)
parser.add_argument("-m", "--min_count", help="The minimum count of the substring", type=int, default=2)
parser.add_argument("-x", "--max_count", help="The maximum count of the substring", type=int, default=None)
parser.add_argument("--version", action="version", version=__version__)
parser.add_argument("-v", "--verbose", action="store_true", help="Print the result to the console")


def main() -> int:
    args = parser.parse_args()

    # if args.version:
    #     from . import __about__
    #     print(__about__.__version__)
    #     return 0

    with open(args.input, "r") as f:
        s = f.read()

    if args.input.endswith(".json"):
        try:
            s = json.loads(s)
        except json.JSONDecodeError:
            print("The input is not a valid JSON file", file=stderr)
            return 1

    result = rstr_max(
        s,
        min_len=args.min_len,
        min_count=args.min_count,
        max_count=args.max_count,
        max_len=args.max_len
    )

    with open(args.output, "w") as f:
        json.dump(result, f, default=lambda x: (x[0], int(x[1])))
        f.write("\n")
        f.flush()
        f.close()

    print(f"Result written to {args.output}, the length of the result is {len(result)}", file=stdout)

    if args.verbose:
        print(result, file=stdout)

    return 0


if __name__ == "__main__":
    exit(main())
