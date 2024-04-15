# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Test repository module."""

import pytest
from pydantic import HttpUrl, ValidationError
from pytest_utils import mock_check_output, mock_temporary_directory, mock_open
from repository import GenericRepository


def test_generic_repository_extra():
    """
    Test GenericRepository when extra attributes are forbidden.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GenericRepository(url='https://example.com/project.git', extra=1)
    assert (
        'extra\n  Extra inputs are not permitted ' +
        '[type=extra_forbidden, input_value=1, input_type=int]\n'
    ) in str(exc_info.value)


def test_generic_repository_url():
    """
    Test GenericRepository url.

    Raises:
        AssertionError: If the test fails.
    """
    repository = GenericRepository(url='https://example.com/project.git')
    assert repository.url == HttpUrl('https://example.com/project.git')


def test_generic_repository_url_parsing():
    """
    Test GenericRepository url when the URL is not valid.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GenericRepository(url='invalid-url')
    assert (
        'url\n  Input should be a valid URL, relative URL without' +
        " a base [type=url_parsing, input_value='invalid-url', " +
        'input_type=str]\n'
    ) in str(exc_info.value)


def test_generic_repository_url_missing():
    """
    Test GenericRepository when the url is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GenericRepository()
    assert (
        'url\n  Field required [type=missing, input_value={}, input_type=dict]'
    ) in str(exc_info.value)


def test_generic_repository_get_file_extra():
    """
    Test GenericRepository get_file when extra arguments are forbidden.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GenericRepository(url='https://example.com/project.git').get_file(
            filename='filename', extra=1,
        )
    assert (
        'extra\n  Unexpected keyword argument ' +
        '[type=unexpected_keyword_argument, input_value=1, input_type=int]'
    ) in str(exc_info.value)


def test_generic_repository_get_file_type():
    """
    Test Project get_file when the filename type is not a string.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GenericRepository(url='https://example.com/project.git').get_file(
            filename=1234.56,
        )
    assert (
        'filename\n  Input should be a valid string [type=string_type, ' +
        'input_value=1234.56, input_type=float]'
    ) in str(exc_info.value)


def test_generic_repository_get_file_empty():
    """
    Test Project get_file when the filename is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GenericRepository(url='https://example.com/project.git').get_file(
            filename='',
        )
    assert (
        'filename\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='', input_type=str]\n"
    ) in str(exc_info.value)


def test_generic_repository_get_file_blank():
    """
    Test Project get_file when the filename is blank.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GenericRepository(url='https://example.com/project.git').get_file(
            filename='   ',
        )
    assert (
        'filename\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='   ', input_type=str]\n"
    ) in str(exc_info.value)


def test_generic_repository_get_file_missing():
    """
    Test Project get_file when the filename is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GenericRepository(url='https://example.com/project.git').get_file()
    assert (
        'filename\n  Missing required argument [type=missing_argument, ' +
        "input_value=ArgsKwargs((GenericReposi...le.com/project.git')),)), " +
        'input_type=ArgsKwargs]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_temporary_directory', 'mock_check_output', 'mock_open')
def test_generic_repository_get_file():
    """
    Test Project get_file.

    Raises:
        AssertionError: If the test fails.
    """
    GenericRepository(url='https://example.com/project.git').get_file('filename')
