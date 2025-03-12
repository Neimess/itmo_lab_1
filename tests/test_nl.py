import os
import re
import sys
from contextlib import redirect_stdout
from io import StringIO

import pytest

from src.nl.nl import NL
from src.nl.nl_main import main as nl_main

SOLUTION_FOLDER_PATH = os.path.join("src", "nl")
RESOURCE_FOLDER_PATH = os.path.join("artifacts", "nl")


@pytest.fixture
def nl():
    return NL()


def parse_nl_helper(output: str):
    pattern = r"^\s*(\d+)\s+(.*)$"
    match = re.match(pattern, output)
    if not match:
        return None

    number = int(match.group(1))
    remaining_string = match.group(2)
    return number, remaining_string


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
        (
            os.path.join(RESOURCE_FOLDER_PATH, "input_3.txt"),
            os.path.join(RESOURCE_FOLDER_PATH, "output_3.txt"),
        ),
    ],
)
def test_compare_lines(input_file: str, output_file: str, monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["nl_main", input_file])
    stdout = StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)
    nl_main()

    output_lines = stdout.getvalue().strip().split("\n")

    with open(output_file, encoding="utf-8") as expected_output_file:
        expected_output_lines = expected_output_file.read().strip().split("\n")

    assert len(output_lines) == len(expected_output_lines), (
        f"The number of lines in the output ({len(output_lines)}) does not match the expected number"
        f"({len(expected_output_lines)})"
    )

    for expected_line, output_line in zip(expected_output_lines, output_lines, strict=False):
        assert parse_nl_helper(expected_line) == parse_nl_helper(output_line), (
            f"\nExpected: {parse_nl_helper(expected_line)}\nReceived : {parse_nl_helper(output_line)}"
        )


def test_nl_stdin(monkeypatch, nl):
    input_data = "\n".join([f"Line {chr(i)}" for i in range(65, 91)])
    expected_output = "\n".join([f"{idx + 1}\tLine {chr(i)}" for idx, i in enumerate(range(65, 91))])

    monkeypatch.setattr(sys, "stdin", StringIO(input_data))
    output = StringIO()
    with redirect_stdout(output):
        nl.process_stream(sys.stdin)
    actual_output = output.getvalue().strip()
    actual_lines = [" ".join(line.split()).replace("\t", " ") for line in actual_output.split("\n")]
    expected_lines = [" ".join(line.split()).replace("\t", " ") for line in expected_output.split("\n")]
    assert actual_lines == expected_lines, f"Wrong output:\nExpected:\n{expected_output}\nGot:\n{actual_output}"


def test_nl_file_not_found(monkeypatch):
    stderr = StringIO()
    monkeypatch.setattr(sys, "argv", ["nl_main", "non_existent_file.txt"])
    monkeypatch.setattr(sys, "stderr", stderr)

    with pytest.raises(SystemExit) as excinfo:
        nl_main()

    assert excinfo.value.code != 0, "The program should exit with an error if the file is missing."

    expected_error = "nl: non_existent_file.txt: No such file or directory"
    stderr_output = stderr.getvalue()

    assert expected_error in stderr_output, f"Expected file not found error, but got:\n{stderr_output}"


def test_nl_file_permission_error(tmp_path, monkeypatch):
    restricted_file = tmp_path / "restricted.txt"
    restricted_file.write_text("Some data")

    restricted_file.chmod(0o000)
    monkeypatch.setattr(sys, "argv", ["nl_main", str(restricted_file)])
    stderr = StringIO()
    monkeypatch.setattr(sys, "stderr", stderr)
    with pytest.raises(SystemExit) as excinfo:
        nl_main()
    restricted_file.chmod(0o644)

    assert excinfo.value.code != 0, "The program should exit with an error on PermissionError."
    stderr_output = stderr.getvalue()
    assert "Permission" in stderr_output, f"Expected permission error in stderr, but got:\n{stderr_output}"
