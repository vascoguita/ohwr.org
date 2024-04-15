# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom Pytest utilities."""


from http import HTTPStatus
from typing import Optional
from urllib.error import URLError

import pytest
from pydantic import BaseModel


class OpenMock(BaseModel):
    """A mock object for handling urllib.request.urlopen and builtins.open."""

    status: Optional[int] = HTTPStatus.OK

    def __enter__(self):
        """
        Enter the context manager.

        Returns:
            OpenMock: The instance of the OpenMock object.
        """
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit the context manager.

        Parameters:
            exc_type: The exception type.
            exc_value: The exception instance.
            exc_traceback: The exception traceback.
        """

    def read(self):
        """
        Read method to retrieve content.

        Returns:
            str: The content of the mock object.
        """
        return 'content'


@pytest.fixture
def mock_urlopen(mocker):
    """
    Fixture for mocking urllib.request.urlopen.

    Parameters:
        mocker: A pytest-mock mocker object.
    """
    mocker.patch('urllib.request.urlopen', return_value=OpenMock())


@pytest.fixture
def mock_urlopen_unreachable(mocker):
    """
    Fixture for mocking unreachable urllib.request.urlopen.

    Parameters:
        mocker: A pytest-mock mocker object.
    """
    mocker.patch(
        'urllib.request.urlopen',
        side_effect=URLError('Mocked URLError'),
    )


@pytest.fixture
def mock_check_output(mocker):
    """
    Fixture for mocking subprocess.check_output.

    Parameters:
        mocker: A pytest-mock mocker object.
    """
    mocker.patch('subprocess.check_output')


@pytest.fixture
def mock_temporary_directory(mocker):
    """
    Fixture for mocking tempfile.mkdtemp.

    Parameters:
        mocker: A pytest-mock mocker object.
    """
    mocker.patch('tempfile.mkdtemp', return_value='dirname')


@pytest.fixture
def mock_open(mocker):
    """
    Fixture for mocking builtins.open.

    Parameters:
        mocker: A pytest-mock mocker object.
    """
    mocker.patch('builtins.open', return_value=OpenMock())
