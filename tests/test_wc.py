import os
import subprocess
from textwrap import dedent

import pytest

SOLUTION_FOLDER_PATH = os.path.join("src", "wc")
RESOURCE_FOLDER_PATH = os.path.join("artifacts", "wc")


@pytest.mark.parametrize(
    "input_files, expected_output",
    [
        (
            [
                os.path.join(RESOURCE_FOLDER_PATH, "input_1.txt"),
                os.path.join(RESOURCE_FOLDER_PATH, "inputBig.txt"),
            ],
            [
                "40  37 121 artifacts/wc/input_1.txt",
                "10702  78451 439742 artifacts/wc/inputBig.txt",
                "10742  78488 439863 total",
            ],
        ),
    ],
)
def test_wc_multiple_files(input_files, expected_output):
    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "wc_main.py"), *input_files],
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"Program exited with error:\n{result.stderr}"

    output_lines = [line.split() for line in result.stdout.strip().split("\n")]
    expected_lines = [line.split() for line in expected_output]

    assert output_lines == expected_lines, f"\nExpected:\n{expected_output}\nGot:\n{result.stdout}"


def test_process_file_permission_error(tmp_path):
    restricted_file = tmp_path / "restricted.txt"
    restricted_file.write_text("Some data")

    restricted_file.chmod(0o000)

    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "wc_main.py"), str(restricted_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    restricted_file.chmod(0o644)

    assert result.returncode != 0, "The program should exit with an error on PermissionError."
    assert f"wc: {restricted_file}: " in result.stderr, (
        f"Expected permission error in stderr, but got:\n{result.stderr}"
    )


@pytest.mark.parametrize(
    "input_file, output_file",
    [
        (
            os.path.join(RESOURCE_FOLDER_PATH, "input_1.txt"),
            os.path.join(RESOURCE_FOLDER_PATH, "output_1.txt"),
        ),
        (
            os.path.join(RESOURCE_FOLDER_PATH, "inputBig.txt"),
            os.path.join(RESOURCE_FOLDER_PATH, "outputBig.txt"),
        ),
    ],
)
def test_compare_lines(input_file: str, output_file: str) -> None:
    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "wc_main.py"), input_file],
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert result.returncode == 0, f"Program exited with error:\n{result.stderr}"

    output_lines = [line.split() for line in result.stdout.strip().split("\n")]

    with open(output_file, encoding="utf-8") as expected_output_file:
        expected_output_lines = [line.split() for line in expected_output_file.read().strip().split("\n")]

    assert len(output_lines) == len(expected_output_lines), (
        f"The number of lines in the output ({len(output_lines)}) does not match the expected number"
        f" ({len(expected_output_lines)})"
    )

    for expected_values, output_values in zip(expected_output_lines, output_lines, strict=False):
        assert expected_values[:3] == output_values[:3], f"\nExpected: {expected_values}\nReceived: {output_values}"


def test_process_file_not_found() -> None:
    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "wc_main.py"), "non_existent_file.txt"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert result.returncode != 0, "The program should exit with an error if the file is missing."
    assert "wc: non_existent_file.txt: No such file or directory" in result.stderr, (
        f"Expected error, but stderr: {result.stderr}"
    )


def test_wc_stdin() -> None:
    input_data = dedent("""
        Lorem ipsum odor amet, consectetuer adipiscing elit.
        Pharetra ullamcorper nec eu nascetur vel.
        Ante mi ipsum orci auctor consequat sapien tristique.
        Est consequat potenti montes, mauris dictum vel ante molestie conubia.
        Ipsum tellus quisque accumsan class elit quam scelerisque cras.
        Ornare platea metus mollis ultrices at odio consectetur suspendisse.
        Condimentum ligula sit tincidunt eros a class aliquam.
        Ultricies integer convallis aenean euismod, dolor finibus.
        Cursus duis porta in himenaeos sem congue elementum.
    """).lstrip()
    expected_output = ["9", "72", "520"]

    result = subprocess.run(
        ["python", os.path.join(SOLUTION_FOLDER_PATH, "wc_main.py")],
        input=input_data,
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )
    output = result.stdout.strip().split()
    assert output == expected_output
