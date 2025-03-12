import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from src.tail.tail_main import main as tail_main

SOLUTION_FOLDER_PATH = os.path.join("src", "tail")
RESOURCE_FOLDER_PATH = os.path.join("artifacts", "tail")


@pytest.mark.parametrize(
    "input_files, expected_output",
    [
        (
            [
                os.path.join(RESOURCE_FOLDER_PATH, "input_1.txt"),
                os.path.join(RESOURCE_FOLDER_PATH, "input_2.txt"),
            ],
            [
                "==> artifacts/tail/input_1.txt <==",
                "aliquam",
                "vitae",
                "justo.",
                "",
                "==> artifacts/tail/input_2.txt <==",
                "xylophone",
                "yellow",
                "zebra",
            ],
        ),
    ],
)
def test_tail_multiple_files(input_files, expected_output, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["tail_main", "-n", "3", *input_files])
    stdout = StringIO()
    with redirect_stdout(stdout):
        tail_main()

    actual_output = stdout.getvalue().strip().split("\n")
    expected_lines = expected_output

    assert actual_output == expected_lines, f"\nExpected:\n{expected_output}\nGot:\n{actual_output}"


@pytest.mark.parametrize(
    "input_file, output_file",
    [
        (
            os.path.join(RESOURCE_FOLDER_PATH, "input_1.txt"),
            os.path.join(RESOURCE_FOLDER_PATH, "output_1.txt"),
        ),
        (
            os.path.join(RESOURCE_FOLDER_PATH, "input_2.txt"),
            os.path.join(RESOURCE_FOLDER_PATH, "output_2.txt"),
        ),
    ],
)
def test_compare_lines(input_file: str, output_file: str, monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["tail_main", input_file])
    stdout = StringIO()
    with redirect_stdout(stdout):
        tail_main()

    actual_output = stdout.getvalue().strip().split("\n")

    with open(output_file, encoding="utf-8") as expected_output_file:
        expected_output_lines = expected_output_file.read().strip().split("\n")

    assert len(actual_output) == len(expected_output_lines), (
        f"The number of lines in the output ({len(actual_output)}) does not match the expected number"
        f" ({len(expected_output_lines)})"
    )

    for expected_line, output_line in zip(expected_output_lines, actual_output, strict=False):
        assert expected_line == output_line, f"\nExpected: {expected_line}\nReceived : {output_line}"


def test_process_file_not_found(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["tail_main", "non_existent_file.txt"])
    stderr = StringIO()
    monkeypatch.setattr(sys, "stderr", stderr)
    with pytest.raises(SystemExit) as excinfo:
        tail_main()

    assert excinfo.value.code != 0, "The program should exit with an error if the file is missing."


def test_tail_missing_file(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["tail_main", "non_existent_file.txt"])
    stderr = StringIO()
    with redirect_stderr(stderr), pytest.raises(SystemExit) as excinfo:
        tail_main()

    assert excinfo.value.code != 0, "Expected non-zero exit code for missing file."


def test_tail_large_n(monkeypatch, tmp_path):
    test_file = tmp_path / "test_large_n.txt"
    test_file.write_text("\n".join([f"Line {i}" for i in range(1, 21)]))

    monkeypatch.setattr(sys, "argv", ["tail_main", "-n", "50", str(test_file)])
    stdout = StringIO()
    with redirect_stdout(stdout):
        tail_main()

    expected_output = "\n".join([f"Line {i}" for i in range(1, 21)])
    assert stdout.getvalue().strip() == expected_output, (
        "Expected entire file content when -n is larger than file size."
    )


def test_tail_invalid_n(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["tail_main", "-n", "invalid"])
    stderr = StringIO()
    with redirect_stderr(stderr), pytest.raises(SystemExit) as excinfo:
        tail_main()

    assert excinfo.value.code != 10, "Expected non zero exit code for invalid -n argument."


def test_tail_stdin(monkeypatch):
    input_data = "\n".join([f"Line {chr(i)}" for i in range(65, 91)])
    expected_output = "\n".join([f"Line {chr(i)}" for i in range(74, 91)])

    monkeypatch.setattr(sys, "stdin", StringIO(input_data))
    monkeypatch.setattr(sys, "argv", ["tail_main"])
    stdout = StringIO()
    with redirect_stdout(stdout):
        tail_main()

    output_lines = stdout.getvalue().strip().split("\n")
    expected_lines = expected_output.strip().split("\n")

    assert output_lines == expected_lines, f"Wrong output:\nExpected:\n{expected_output}\nGot:\n{stdout.getvalue()}"


def test_tail_empty_file(monkeypatch, tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()

    monkeypatch.setattr(sys, "argv", ["tail_main", str(empty_file)])
    stdout = StringIO()
    with redirect_stdout(stdout):
        tail_main()

    assert stdout.getvalue().strip() == "", "Empty file should produce no output"


def test_tail_missing_n_argument(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["tail_main", "-n"])
    stderr = StringIO()
    with redirect_stderr(stderr), pytest.raises(SystemExit) as excinfo:
        tail_main()

    assert excinfo.value.code != 0, "Expected non zero exit code when `-n` is used without argument."


def test_tail_invalid_n_argument(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["tail_main", "-n", "abc"])
    stderr = StringIO()
    with redirect_stderr(stderr), pytest.raises(SystemExit) as excinfo:
        tail_main()

    assert excinfo.value.code == 1, "Expected exit code 1 when `-n` is given an invalid number."
