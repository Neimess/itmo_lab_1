import os
import re
import subprocess
import sys
from io import StringIO

import pytest

SOLUTION_FOLDER_PATH = os.path.join("src", "nl")
RESOURCE_FOLDER_PATH = os.path.join("artifacts", "nl")


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
def test_compare_lines(input_file: str, output_file: str) -> None:
    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "nl_main.py"), input_file],
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )

    output_lines = result.stdout.strip().split("\n")

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


def test_process_file_not_found():
    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "nl_main.py"), "non_existent_file.txt"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert result.returncode != 0, "The program should exit with an error if the file is missing."
    assert "nl: non_existent_file.txt: No such file or directory" in result.stderr, (
        f"Expected error, but stderr: {result.stderr}"
    )


def test_nl_stdin(monkeypatch):
    input_data = "\n".join([f"Line {chr(i)}" for i in range(65, 91)])
    expected_output = "\n".join([f"{idx + 1}\tLine {chr(i)}" for idx, i in enumerate(range(65, 91))])

    monkeypatch.setattr(sys, "stdin", StringIO(input_data))

    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "nl_main.py")],
        input=input_data,
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )
    output_lines = [line.strip() for line in result.stdout.strip().split("\n")]
    expected_lines = [line.strip() for line in expected_output.strip().split("\n")]

    assert output_lines == expected_lines, f"Wrong output:\nExpected:\n{expected_output}\nGot:\n{result.stdout}"


def test_nl_file_not_found():
    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "nl_main.py"), "non_existent_file.txt"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert result.returncode != 0, "The program should exit with an error if the file is missing."
    assert "nl: non_existent_file.txt: No such file or directory" in result.stderr, (
        f"Expected file not found error, but got:\n{result.stderr}"
    )


def test_nl_file_permission_error(tmp_path):
    restricted_file = tmp_path / "restricted.txt"
    restricted_file.write_text("Some data")

    restricted_file.chmod(0o000)

    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "nl_main.py"), str(restricted_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    restricted_file.chmod(0o644)

    assert result.returncode != 0, "The program should exit with an error on PermissionError."
    assert f"nl: {restricted_file}: " in result.stderr, (
        f"Expected permission error in stderr, but got:\n{result.stderr}"
    )
