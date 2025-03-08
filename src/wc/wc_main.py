import sys

from wc import WC


def main() -> None:
    wc = WC()
    wc.process_data(sys.argv[1:])


if __name__ == "__main__":
    main()
