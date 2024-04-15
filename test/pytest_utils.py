# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom Pytest utilities."""


from http import HTTPStatus
from typing import Optional
from urllib.error import URLError

from pydantic import BaseModel
import pytest


class OpenMock(BaseModel):
    status: Optional[int] = HTTPStatus.OK

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass


@pytest.fixture
def mock_urlopen(mocker):
    mocker.patch('urllib.request.urlopen', return_value=OpenMock())


@pytest.fixture
def mock_urlopen_unreachable(mocker):
    mocker.patch(
        'urllib.request.urlopen',
        side_effect=URLError('Mocked URLError'),
    )


@pytest.fixture
def mock_check_output(mocker):
    mocker.patch('subprocess.check_output')


@pytest.fixture
def mock_temporary_directory(mocker):
    mocker.patch('tempfile.mkdtemp', return_value='dirname')


@pytest.fixture
def mock_open(mocker):
    mocker.patch('builtins.open', return_value=OpenMock())
