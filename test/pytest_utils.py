# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom Pytest utilities."""


import subprocess  # noqa: S404
from http import HTTPStatus
from typing import Optional
from urllib.error import URLError

import pytest
from pydantic import BaseModel


class OpenURLMock(BaseModel):
    """Mock class for urllib.request.urlopen."""

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
        Return mocked content as bytes.

        Returns:
            bytes: The mocked content encoded as bytes.
        """
        return 'mock_content'.encode()


@pytest.fixture
def mock_urlopen(mocker):
    """
    Fixture for mocking urllib.request.urlopen.

    Parameters:
        mocker: A pytest-mock mocker object.
    """
    mocker.patch('urllib.request.urlopen', return_value=OpenURLMock())


@pytest.fixture
def mock_urlopen_error(mocker):
    """
    Fixture for mocking a urllib.request.urlopen failure.

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
def mock_check_output_error(mocker):
    """
    Fixture for mocking a subprocess.check_output failure.

    Parameters:
        mocker: A pytest-mock mocker object.
    """
    mocker.patch(
        'subprocess.check_output',
        side_effect=subprocess.CalledProcessError(
            1, 'Mocked CalledProcessError',
        ),
    )


@pytest.fixture
def mock_temporary_directory(mocker):
    """
    Fixture for mocking tempfile.mkdtemp.

    Parameters:
        mocker: A pytest-mock mocker object.
    """
    mocker.patch('tempfile.mkdtemp', return_value='mock_dirname')


@pytest.fixture
def mock_open(mocker):
    """
    Fixture for mocking builtins.open.

    Parameters:
        mocker: A pytest-mock mocker object.
    """
    mocker.patch('builtins.open', mocker.mock_open(read_data='mock_content'))


@pytest.fixture
def mock_open_error(mocker):
    """
    Fixture for mocking a builtins.open failure.

    Parameters:
        mocker: A pytest-mock mocker object.
    """
    mocker.patch(
        'builtins.open',
        side_effect=FileNotFoundError('Mocked FileNotFoundError'),
    )
