# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Test repository module."""

import pytest
from pydantic import HttpUrl, ValidationError
from repository import GenericRepository, GitHubRepository, Repository


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
