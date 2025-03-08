import os
import subprocess

import pytest

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
def test_tail_multiple_files(input_files, expected_output):
    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "tail_main.py"), "-n", "3", *input_files],
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"Program exited with error:\n{result.stderr}"

    output_lines = result.stdout.strip().split("\n")
    expected_lines = expected_output

    assert output_lines == expected_lines, f"\nExpected:\n{expected_output}\nGot:\n{result.stdout}"


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
def test_compare_lines(input_file: str, output_file: str) -> None:
    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "tail_main.py"), input_file],
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )

    output_lines = result.stdout.strip().split("\n")

    with open(output_file, encoding="utf-8") as expected_output_file:
        expected_output_lines = expected_output_file.read().strip().split("\n")

    assert len(output_lines) == len(expected_output_lines), (
        f"The number of lines in the output ({len(output_lines)}) does not match the expected number"
        f" ({len(expected_output_lines)})"
    )

    for expected_line, output_line in zip(expected_output_lines, output_lines, strict=False):
        assert expected_line == output_line, f"\nExpected: {expected_line}\nReceived : {output_line}"


def test_process_file_not_found():
    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "tail_main.py"), "non_existent_file.txt"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert result.returncode != 0, "The program should exit with an error if the file is missing."
    assert "tail: non_existent_file.txt: No such file or directory" in result.stderr, (
        f"Expected error, but stderr: {result.stderr}"
    )


def test_process_file_permission_error(tmp_path):
    restricted_file = tmp_path / "restricted.txt"
    restricted_file.write_text("Some data")

    restricted_file.chmod(0o000)

    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "tail_main.py"), str(restricted_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    restricted_file.chmod(0o644)

    assert result.returncode != 0, "The program should exit with an error on PermissionError."
    assert f"tail: {restricted_file}: " in result.stderr, (
        f"Expected permission error in stderr, but got:\n{result.stderr}"
    )


def test_tail_n(tmp_path):
    test_file = tmp_path / "test_n.txt"
    test_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n", encoding="utf-8")

    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "tail_main.py"), "-n", "3", str(test_file)],
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )

    expected_output = "Line 3\nLine 4\nLine 5\n"

    assert result.stdout.strip() == expected_output.strip(), f"Wrong output: {result.stdout}"


def test_tail_stdin():
    input_data = "\n".join([f"Line {chr(i)}" for i in range(65, 91)])
    expected_output = "\n".join([f"Line {chr(i)}" for i in range(74, 91)])

    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "tail_main.py")],
        input=input_data,
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )
    output_lines = [line.strip() for line in result.stdout.strip().split("\n")]
    expected_lines = [line.strip() for line in expected_output.strip().split("\n")]

    assert output_lines == expected_lines, f"Wrong output:\nExpected:\n{expected_output}\nGot:\n{result.stdout}"


def test_tail_empty_file(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()

    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "tail_main.py"), str(empty_file)],
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert result.stdout.strip() == "", "Empty file should produce no output"


def test_tail_missing_n_argument():
    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "tail_main.py"), "-n"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert result.returncode == 1, "Expected exit code 1 when `-n` is used without argument."
    assert "tail: invalid number of lines:" in result.stderr, f"Expected usage error message, got: {result.stderr}"


def test_tail_invalid_n_argument():
    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "tail_main.py"), "-n", "abc"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert result.returncode == 1, "Expected exit code 1 when `-n` is given an invalid number."
    assert "tail: invalid number of lines: abc" in result.stderr, (
        f"Expected invalid number error message, got: {result.stderr}"
    )
