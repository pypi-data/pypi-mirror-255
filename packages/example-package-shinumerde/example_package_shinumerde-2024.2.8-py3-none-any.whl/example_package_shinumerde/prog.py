import argparse

from collections import Counter
from functools import lru_cache


@lru_cache
def collection(seq):
    return sum(1 for count in Counter(seq).values() if count == 1)


def process_string(string):
    result = collection(string)
    print(result)
    return result


def process_file(file):
    try:
        with open(file, 'r') as f:
            content = f.read()
            result = collection(content)
            print(result)
            return result
    except FileNotFoundError:
        print(f"Error: File '{file}' not found.")


def arg_parser():
    parser = argparse.ArgumentParser(
        prog='CLI',
        description="Count unique chars in sequence, please choose what you want to count.",
        usage="Type --string for a string or --file for a file with a string.",
        conflict_handler='error')
    parser.add_argument(
        "--string",
        type=str,
        help="Input a string for counting unique chars.")
    parser.add_argument(
        "--file",
        type=str,
        help="Input a file with a sequence for counting unique chars.")
    return parser


def main():
    parser = arg_parser()
    args, unknown = parser.parse_known_args()
    if args.file:
        return process_file(args.file)
    elif args.string:
        return process_string(args.string)
    else:
        return parser.print_help()


if __name__ == '__main__':
    main()
