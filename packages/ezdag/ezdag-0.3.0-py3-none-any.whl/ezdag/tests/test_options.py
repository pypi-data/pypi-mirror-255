import pytest

from ..options import Argument, Literal, Option
from .. import path


@pytest.mark.parametrize(
    "name,value,is_file",
    [
        ["index", 1, False],
        ["format", "csv", False],
        ["input", "file1.txt", True],
        ["input", "to/file1.txt", True],
        ["input", "/path/to/file1.txt", True],
    ],
)
def test_argument_commands_single(name, value, is_file):
    argument = Argument(name, value)

    assert argument.name == name
    assert argument.vars() == str(value)

    if is_file:
        assert argument.files() == value

        filename = path.normalize(value, basename=path.is_abs_or_url)
        assert argument.files(basename=path.is_abs_or_url) == filename

        if filename == value:
            assert not argument.remaps()
        else:
            assert argument.remaps() == f"{filename}={value}"


def test_option_commands_flag():
    name = "verbose"
    option = Option(name)

    assert option.name == name
    assert option.vars() == f"--{name}"


@pytest.mark.parametrize(
    "name,value,is_file",
    [
        ["index", 1, False],
        ["format", "csv", False],
        ["input", "file1.txt", True],
        ["input", "to/file1.txt", True],
        ["input", "/path/to/file1.txt", True],
    ],
)
def test_option_commands_single(name, value, is_file):
    option = Option(name, value)

    assert option.name == name
    assert option.vars() == f"--{name} {value}"

    if is_file:
        assert option.files() == value

        filename = path.normalize(value, basename=path.is_abs_or_url)
        assert option.files(basename=path.is_abs_or_url) == filename

        if filename == value:
            assert not option.remaps()
        else:
            assert option.remaps() == f"{filename}={value}"


@pytest.mark.parametrize(
    "value,is_file",
    [
        [1, False],
        ["csv", False],
        ["file1.txt", True],
        ["to/file1.txt", True],
        ["/path/to/file1.txt", True],
    ],
)
def test_literal_commands_single(value, is_file):
    literal = Literal(value)

    assert literal.vars() == str(value)

    if is_file:
        assert literal.files() == str(value)

        filename = path.normalize(value, basename=path.is_abs_or_url)
        assert literal.files(basename=path.is_abs_or_url) == filename

        if filename == value:
            assert not literal.remaps()
        else:
            assert literal.remaps() == f"{filename}={value}"
