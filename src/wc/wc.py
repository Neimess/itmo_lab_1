import sys
from typing import NoReturn, TextIO


class WC:
    def __init__(self) -> None:
        self.total_lines: int = 0
        self.total_words: int = 0
        self.total_bytes: int = 0

    def _process_file(self, filename: str) -> tuple[int, int, int]:
        lines = words = bytes_count = 0
        try:
            with open(filename, encoding="utf-8") as file:
                for line in file:
                    lines += 1
                    words += len(line.split())
                    bytes_count += len(line.encode("utf-8"))
        except FileNotFoundError:
            print(f"wc: {filename}: No such file or directory", file=sys.stderr)
            self._exit_with_error()
        except Exception as e:
            print(f"wc: {filename}: {e}", file=sys.stderr)
            self._exit_with_error()

        self.total_lines += lines
        self.total_words += words
        self.total_bytes += bytes_count

        return lines, words, bytes_count

    def _process_stdin(self, stream: TextIO) -> tuple[int, int, int]:
        lines = words = bytes_count = 0
        for line in stream:
            lines += 1
            words += len(line.split())
            bytes_count += len(line.encode("utf-8"))
        self.total_lines += lines
        self.total_words += words
        self.total_bytes += bytes_count
        return lines, words, bytes_count

    def _exit_with_error(self) -> NoReturn:
        sys.exit(-1)

    def process_data(self, filenames: list[str]) -> None:
        results = []

        if not filenames:
            lines, words, bytes_count = self._process_stdin(sys.stdin)
            results.append((lines, words, bytes_count, ""))
        else:
            for filename in filenames:
                lines, words, bytes_count = self._process_file(filename)
                results.append((lines, words, bytes_count, filename))
        if len(filenames) > 1:
            results.append((self.total_lines, self.total_words, self.total_bytes, "total"))
        max_lines_width = max(len(str(lines)) for lines, _, _, _ in results)
        max_words_width = max(len(str(words)) for _, words, _, _ in results)
        max_bytes_width = max(len(str(bytes_count)) for _, _, bytes_count, _ in results)

        for lines, words, bytes_count, filename in results:
            print(
                f"{lines:{max_lines_width}d} {words:{max_words_width}d} "
                f"{bytes_count:{max_bytes_width}d} {filename}".rstrip()
            )
