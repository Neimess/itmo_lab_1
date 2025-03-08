import sys

from nl import NL


def main() -> None:
    nl_instance = NL()

    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            nl_instance.process_file(filename)
    else:
        nl_instance.process_stream(sys.stdin)


if __name__ == "__main__":
    main()
