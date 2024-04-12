# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom Pytest utilities."""


from http import HTTPStatus
from unittest.mock import MagicMock, Mock, patch
from urllib.error import URLError

import pytest


@pytest.fixture
def mock_urlopen():
    """
    Fixture for mocking urlopen requests.

    Yields:
        MagicMock: A mock object for urlopen requests.
    """
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = Mock()
        mock_urlopen.return_value.__enter__.return_value.status = HTTPStatus.OK
        yield mock_urlopen


@pytest.fixture
def mock_urlopen_unreachable():
    """
    Fixture for mocking unreachable urlopen requests.

    Yields:
        MagicMock: A mock object for urlopen requests that raise URLError.
    """
    with patch('urllib.request.urlopen') as mock_urlopen:
        mock_urlopen.side_effect = URLError('Mocked URLError')
        yield mock_urlopen


@pytest.fixture
def mock_check_output():
    """
    Fixture to mock the subprocess.check_output function.

    Yields:
        MagicMock: A mock object for the subprocess.check_output function.
    """
    with patch('subprocess.check_output') as mock_check_output:
        yield mock_check_output


@pytest.fixture
def mock_temporary_directory():
    """
    Fixture to mock the tempfile.TemporaryDirectory function.

    Yields:
        MagicMock: A mock object for the tempfile.TemporaryDirectory.
    """
    with patch('tempfile.TemporaryDirectory') as mock_temporary_directory:
        mock_temporary_directory.return_value = MagicMock()
        mock_temporary_directory.return_value.name = 'mock_temp_dir'
        yield mock_temporary_directory