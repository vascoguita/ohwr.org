# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom Pytest utilities."""


from http import HTTPStatus
from unittest.mock import Mock, patch
from urllib import request
from urllib.error import URLError

import pytest


@pytest.fixture
def mock_urlopen_successful():
    """
    Fixture for mocking successful urlopen requests.

    Yields:
        MagicMock: A mock object for successful urlopen requests.
    """
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response
        yield mock_urlopen


@pytest.fixture
def mock_urlopen_unreachable():
    """
    Fixture for mocking unreachable urlopen requests.

    Yields:
        MagicMock: A mock object for urlopen requests that raise URLError.
    """
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_urlopen.side_effect = URLError('Mocked URLError')
        yield mock_urlopen
