from collections import Counter
from functools import lru_cache
from argparse import ArgumentParser


@lru_cache(maxsize=8)
def _count_authentic_signs(string):
    counter = Counter(string)
    number_of_signs = len([significance for significance in counter.values() if significance == 1])
    return number_of_signs


def count_authentic_signs(string):
    if not isinstance(string, str):
        raise TypeError("Input text, please")
    return _count_authentic_signs(string)


def read_file(file):
    if file is None:
        raise ValueError("File is not provided.")
    try:
        with open(file, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError("File not found. Please check the file path.")


def cli():
    parser = ArgumentParser(description='Command Line Interface')
    parser.add_argument('--string', type=str, help='Input a text')
    parser.add_argument('--file', type=str, help='Specify the path to the file')
    args = parser.parse_args()
    result = None
    if args.file is not None:
        result = count_authentic_signs(read_file(args.file))
    elif args.string is not None:
        result = count_authentic_signs(args.string)
    print(result)
    return result


if __name__ == '__main__':
    cli()
