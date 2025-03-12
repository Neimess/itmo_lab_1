import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from src.wc.wc_main import main as wc_main

SOLUTION_FOLDER_PATH = os.path.join("src", "wc")
RESOURCE_FOLDER_PATH = os.path.join("artifacts", "wc")


def test_wc_multiple_files(monkeypatch):
    input_files = [
        os.path.join(RESOURCE_FOLDER_PATH, "input_1.txt"),
        os.path.join(RESOURCE_FOLDER_PATH, "inputBig.txt"),
    ]
    expected_output = [
        "40  37 121 artifacts/wc/input_1.txt",
        "10702  78451 439742 artifacts/wc/inputBig.txt",
        "10742  78488 439863 total",
    ]

    monkeypatch.setattr(sys, "argv", ["wc_main", *input_files])
    stdout = StringIO()
    with redirect_stdout(stdout):
        wc_main()

    output_lines = [line.split() for line in stdout.getvalue().strip().split("\n")]
    expected_lines = [line.split() for line in expected_output]

    assert output_lines == expected_lines, f"\nExpected:\n{expected_output}\nGot:\n{stdout.getvalue()}"


def test_process_file_permission_error(monkeypatch, tmp_path):
    restricted_file = tmp_path / "restricted.txt"
    restricted_file.write_text("Some data")
    restricted_file.chmod(0o000)

    monkeypatch.setattr(sys, "argv", ["wc_main", str(restricted_file)])
    stderr = StringIO()
    with redirect_stderr(stderr), pytest.raises(SystemExit) as excinfo:
        wc_main()

    restricted_file.chmod(0o644)

    assert excinfo.value.code != 0, "Expected non-zero exit code for permission error."
    assert f"wc: {restricted_file}: " in stderr.getvalue(), (
        f"Expected permission error in stderr, but got:\n{stderr.getvalue()}"
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
def test_compare_lines(monkeypatch, input_file: str, output_file: str):
    monkeypatch.setattr(sys, "argv", ["wc_main", input_file])
    stdout = StringIO()
    with redirect_stdout(stdout):
        wc_main()

    output_lines = [line.split() for line in stdout.getvalue().strip().split("\n")]

    with open(output_file, encoding="utf-8") as expected_output_file:
        expected_output_lines = [line.split() for line in expected_output_file.read().strip().split("\n")]

    assert len(output_lines) == len(expected_output_lines), (
        f"The number of lines in the output ({len(output_lines)}) does not match the expected number"
        f" ({len(expected_output_lines)})"
    )

    for expected_values, output_values in zip(expected_output_lines, output_lines, strict=False):
        assert expected_values == output_values, f"\nExpected: {expected_values}\nReceived: {output_values}"


def test_process_file_not_found(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["wc_main", "non_existent_file.txt"])
    stderr = StringIO()
    with redirect_stderr(stderr), pytest.raises(SystemExit) as excinfo:
        wc_main()

    assert excinfo.value.code != 0, "The program should exit with an error if the file is missing."


def test_wc_stdin(monkeypatch):
    input_data = """
        Lorem ipsum odor amet, consectetuer adipiscing elit.
        Pharetra ullamcorper nec eu nascetur vel.
        Ante mi ipsum orci auctor consequat sapien tristique.
        Est consequat potenti montes, mauris dictum vel ante molestie conubia.
        Ipsum tellus quisque accumsan class elit quam scelerisque cras.
        Ornare platea metus mollis ultrices at odio consectetur suspendisse.
        Condimentum ligula sit tincidunt eros a class aliquam.
        Ultricies integer convallis aenean euismod, dolor finibus.
        Cursus duis porta in himenaeos sem congue elementum.
    """.strip()
    expected_output = ["9", "72", "583"]

    monkeypatch.setattr(sys, "stdin", StringIO(input_data))
    monkeypatch.setattr(sys, "argv", ["wc_main"])
    stdout = StringIO()
    with redirect_stdout(stdout):
        wc_main()

    output = stdout.getvalue().strip().split()
    assert output == expected_output, f"Expected:\n{expected_output}\nGot:\n{stdout.getvalue()}"
