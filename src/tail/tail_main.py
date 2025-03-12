import sys

from src.tail.tail import Tail


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] == "-n":
        if len(args) < 3:
            print("tail: invalid number of lines", file=sys.stderr)
            sys.exit(1)

        try:
            num_lines = int(args[1])
        except ValueError:
            print(f"tail: invalid number of lines: {args[1]}", file=sys.stderr)
            sys.exit(1)

        tail = Tail(num_lines)
        files = args[2:]
    else:
        tail = Tail()
        files = args

    if not files:
        tail.process_stream(sys.stdin)
        return

    multiple_files = len(files) > 1

    for i, file in enumerate(files):
        tail.process_file(file, multiple_files)
        if i < len(files) - 1:
            print()


if __name__ == "__main__":
    main()
