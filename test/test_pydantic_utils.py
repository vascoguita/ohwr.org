# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Test pydantic_utils module."""

from http import HTTPStatus
from unittest.mock import Mock, patch
from urllib import request
from urllib.error import URLError

import pytest
from pydantic import BaseModel, HttpUrl, ValidationError
from pydantic_utils import (
    AnnotatedStr,
    AnnotatedStrList,
    BaseModelForbidExtra,
    Url,
    UrlList,
)


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


class BaseModelForbidExtraTest(BaseModelForbidExtra):
    """Test class for BaseModelForbidExtra."""

    test_attribute: int


def test_base_model_forbid_extra():
    """
    Test case for BaseModelForbidExtra class.

    Raises:
        AssertionError: If the test fails.
    """
    test_object = BaseModelForbidExtraTest(test_attribute=1)
    assert test_object.test_attribute == 1


def test_base_model_forbid_extra_missing():
    """
    Test BaseModelForbidExtra when attribute is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        BaseModelForbidExtraTest()
    assert (
        'test_attribute\n  Field required ' +
        '[type=missing, input_value={}, input_type=dict]\n'
    ) in str(exc_info.value)


def test_base_model_forbid_extra_forbidden():
    """
    Test BaseModelForbidExtra when extra attributes are forbidden.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        BaseModelForbidExtraTest(test_attribute=1, extra_attribute=2)
    assert (
        'extra_attribute\n  Extra inputs are not permitted ' +
        '[type=extra_forbidden, input_value=2, input_type=int]\n'
    ) in str(exc_info.value)


class AnnotatedStrTest(BaseModel):
    """Test class for AnnotatedStr."""

    test_attribute: AnnotatedStr


def test_annotated_str():
    """
    Test case for AnnotatedStr type.

    Raises:
        AssertionError: If the test fails.
    """
    test_object = AnnotatedStrTest(test_attribute='Hello World')
    assert test_object.test_attribute == 'Hello World'


def test_annotated_str_type():
    """
    Test AnnotatedStr when the type is not a string.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        AnnotatedStrTest(test_attribute=1234.56)
    assert (
        'test_attribute\n  Input should be a valid string ' +
        '[type=string_type, input_value=1234.56, input_type=float]\n'
    ) in str(exc_info.value)


def test_annotated_str_empty():
    """
    Test AnnotatedStr when the string is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        AnnotatedStrTest(test_attribute='')
    assert (
        'test_attribute\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='', input_type=str]\n"
    ) in str(exc_info.value)


def test_annotated_str_blank():
    """
    Test AnnotatedStr when the string is blank.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        AnnotatedStrTest(test_attribute='   ')
    assert (
        'test_attribute\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='   ', input_type=str]\n"
    ) in str(exc_info.value)


class AnnotatedStrListTest(BaseModel):
    """Test class for AnnotatedStrList."""

    test_attribute: AnnotatedStrList


def test_annotated_str_list():
    """
    Test case for AnnotatedStrList type.

    Raises:
        AssertionError: If the test fails.
    """
    test_object = AnnotatedStrListTest(test_attribute=['Hello World'])
    assert test_object.test_attribute == ['Hello World']


def test_annotated_str_list_type():
    """
    Test AnnotatedStrList when the type is not a list.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        AnnotatedStrListTest(test_attribute='abcd')
    assert (
        'test_attribute\n  Input should be a valid list ' +
        "[type=list_type, input_value='abcd', input_type=str]\n"
    ) in str(exc_info.value)


def test_annotated_str_list_empty():
    """
    Test AnnotatedStrList when the list is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        AnnotatedStrListTest(test_attribute=[])
    assert (
        'test_attribute\n  List should have at least 1 item after ' +
        'validation, not 0 [type=too_short, input_value=[], input_type=list]\n'
    ) in str(exc_info.value)


class UrlTest(BaseModel):
    """Test class for Url."""

    test_attribute: Url


def test_url(mock_urlopen_successful):
    """
    Test case for Url type.

    Parameters:
        mock_urlopen_successful: A fixture providing mocked urlopen.

    Raises:
        AssertionError: If the test fails.
    """
    test_object = UrlTest(test_attribute='https://reachable.com')
    assert test_object.test_attribute == HttpUrl('https://reachable.com')


def test_url_parsing(mock_urlopen_successful):
    """
    Test Url when the URL is not valid.

    Parameters:
        mock_urlopen_successful: A fixture providing mocked urlopen.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        UrlTest(test_attribute='invalid-url')
    assert (
        'test_attribute\n  Input should be a valid URL, relative URL without' +
        " a base [type=url_parsing, input_value='invalid-url', " +
        'input_type=str]\n'
    ) in str(exc_info.value)


def test_url_unreachable(mock_urlopen_unreachable):
    """
    Test Url when the URL is not reachable.

    Parameters:
        mock_urlopen_unreachable: A fixture providing mocked urlopen.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        UrlTest(test_attribute='https://unreachable.com')
    assert (
        'test_attribute\n  Value error, Failed to access URL: ' +
        "'https://unreachable.com/'. [type=value_error, " +
        "input_value='https://unreachable.com', input_type=str]\n"
    ) in str(exc_info.value)


class UrlListTest(BaseModel):
    """Test class for UrlList."""

    test_attribute: UrlList


def test_url_list(mock_urlopen_successful):
    """
    Test case for UrlList type.

    Parameters:
        mock_urlopen_successful: A fixture providing mocked urlopen.

    Raises:
        AssertionError: If the test fails.
    """
    test_object = UrlListTest(test_attribute=['https://reachable.com'])
    assert test_object.test_attribute == [HttpUrl('https://reachable.com')]


def test_url_list_type(mock_urlopen_successful):
    """
    Test UrlList when the type is not a list.

    Parameters:
        mock_urlopen_successful: A fixture providing mocked urlopen.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        UrlListTest(test_attribute='abcd')
    assert (
        'test_attribute\n  Input should be a valid list ' +
        "[type=list_type, input_value='abcd', input_type=str]\n"
    ) in str(exc_info.value)


def test_url_list_empty(mock_urlopen_successful):
    """
    Test UrlList when the list is empty.

    Parameters:
        mock_urlopen_successful: A fixture providing mocked urlopen.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        UrlListTest(test_attribute=[])
    assert (
        'test_attribute\n  List should have at least 1 item after ' +
        'validation, not 0 [type=too_short, input_value=[], input_type=list]\n'
    ) in str(exc_info.value)
