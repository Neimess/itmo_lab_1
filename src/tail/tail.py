import sys
from typing import NoReturn, TextIO


class Tail:
    def __init__(self, num_lines: int = 17) -> None:
        self.num_lines: int = num_lines

    def process_file(self, filename: str, multiple_files: bool = False) -> None:
        try:
            with open(filename, encoding="utf-8") as file:
                lines: list[str] = file.readlines()
            if multiple_files:
                self._print_file_header(filename)
            self._print_tail(lines)
        except FileNotFoundError:
            print(f"tail: {filename}: No such file or directory", file=sys.stderr)
            self._exit_with_error()
        except Exception as e:
            print(f"tail: {filename}: {e}", file=sys.stderr)
            self._exit_with_error()

    def process_stream(self, stream: TextIO) -> None:
        lines: list[str] = stream.readlines()
        self._print_tail(lines)

    def _print_file_header(self, filename: str) -> None:
        print(f"==> {filename} <==", flush=True)

    def _print_tail(self, lines: list[str]) -> None:
        for line in lines[-self.num_lines :]:
            print(line, end="", flush=True)

    def _exit_with_error(self) -> NoReturn:
        sys.exit(-1)
