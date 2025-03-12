import sys
from typing import NoReturn, TextIO


class NL:
    def __init__(self) -> None:
        self.line_number: int = 1

    def process_file(self, filename: str) -> None:
        try:
            with open(filename, encoding="utf-8") as file:
                lines: list[str] = file.readlines()
                self._print_lines(lines)
        except FileNotFoundError:
            print(f"nl: {filename}: No such file or directory", file=sys.stderr)
            self._exit_with_error()
        except Exception as e:
            print(f"nl: {filename}: {e}", file=sys.stderr)
            self._exit_with_error()

    def process_stream(self, stream: TextIO) -> None:
        try:
            lines: list[str] = stream.readlines()
            self._print_lines(lines)
        except Exception as e:
            print(f"nl: error reading from stream: {e}", file=sys.stderr)
            self._exit_with_error()

    def _print_lines(self, lines: list[str]) -> None:
        max_number_length: int = len(str(self.line_number + len(lines) - 1))
        for line in lines:
            print(f"{str(self.line_number).rjust(max_number_length)}\t{line.rstrip()}", flush=True)
            self.line_number += 1

    def _exit_with_error(self) -> NoReturn:
        sys.exit(-1)
