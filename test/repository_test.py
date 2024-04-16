# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Test repository module."""

import pytest
from pydantic import HttpUrl, ValidationError
from pytest_utils import (
    mock_check_output,
    mock_check_output_error,
    mock_open,
    mock_open_error,
    mock_temporary_directory,
    mock_urlopen,
    mock_urlopen_error,
)
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
    Test GenericRepository get_file when the filename type is not a string.

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
    Test GenericRepository get_file when the filename is empty.

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
    Test GenericRepository get_file when the filename is blank.

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
    Test GenericRepository get_file when the filename is missing.

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


@pytest.mark.usefixtures(
    'mock_temporary_directory', 'mock_check_output', 'mock_open',
)
def test_generic_repository_get_file():
    """
    Test GenericRepository get_file.

    Raises:
        AssertionError: If the test fails.
    """
    repository = GenericRepository(url='https://example.com/project.git')
    assert repository.get_file('filename') == 'mock_content'


@pytest.mark.usefixtures('mock_temporary_directory', 'mock_check_output_error')
def test_generic_repository_get_file_clone_error():
    """
    Test GenericRepository get_file when the clone fails.

    Raises:
        AssertionError: If the test fails.
    """
    repository = GenericRepository(url='https://example.com/project.git')
    with pytest.raises(RuntimeError) as exc_info:
        repository.get_file('filename')
    assert (
        "Failed to clone 'https://example.com/project.git':\n" +
        "Command 'Mocked CalledProcessError' returned non-zero exit status 1."
    ) in str(exc_info.value)


@pytest.mark.usefixtures(
    'mock_temporary_directory', 'mock_check_output', 'mock_open_error',
)
def test_generic_repository_get_file_open_error():
    """
    Test GenericRepository get_file when the open fails.

    Raises:
        AssertionError: If the test fails.
    """
    repository = GenericRepository(url='https://example.com/project.git')
    with pytest.raises(ValueError) as exc_info:
        repository.get_file('filename')
    assert (
        "'filename' not found in 'https://example.com/project.git':\n" +
        'Mocked FileNotFoundError'
    ) in str(exc_info.value)


def test_github_repository_extra():
    """
    Test GitHubRepository when extra attributes are forbidden.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='owner', repo='repo', extra=1)
    assert (
        'extra\n  Extra inputs are not permitted ' +
        '[type=extra_forbidden, input_value=1, input_type=int]\n'
    ) in str(exc_info.value)


def test_github_repository_owner():
    """
    Test GitHubRepository owner.

    Raises:
        AssertionError: If the test fails.
    """
    repository = GitHubRepository(owner='owner', repo='repo')
    assert repository.owner == 'owner'


def test_github_repository_owner_type():
    """
    Test GitHubRepository owner when the type is not a string.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner=1234.56, repo='repo')
    assert (
        'owner\n  Input should be a valid string ' +
        '[type=string_type, input_value=1234.56, input_type=float]\n'
    ) in str(exc_info.value)


def test_github_repository_owner_empty():
    """
    Test GitHubRepository when the owner is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='', repo='repo')
    assert (
        'owner\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='', input_type=str]\n"
    ) in str(exc_info.value)


def test_github_repository_owner_blank():
    """
    Test GitHubRepository when the owner is blank.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='   ', repo='repo')
    assert (
        'owner\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='   ', input_type=str]\n"
    ) in str(exc_info.value)


def test_github_repository_owner_missing():
    """
    Test GitHubRepository when the owner is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(repo='repo')
    assert (
        '1 validation error for GitHubRepository\nowner\n  Field required ' +
        "[type=missing, input_value={'repo': 'repo'}, input_type=dict]"
    ) in str(exc_info.value)


def test_github_repository_repo():
    """
    Test GitHubRepository repo.

    Raises:
        AssertionError: If the test fails.
    """
    repository = GitHubRepository(owner='owner', repo='repo')
    assert repository.repo == 'repo'


def test_github_repository_repo_type():
    """
    Test GitHubRepository repo when the type is not a string.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='owner', repo=1234.56)
    assert (
        'repo\n  Input should be a valid string ' +
        '[type=string_type, input_value=1234.56, input_type=float]\n'
    ) in str(exc_info.value)


def test_github_repository_repo_empty():
    """
    Test GitHubRepository when the repo is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='owner', repo='')
    assert (
        'repo\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='', input_type=str]\n"
    ) in str(exc_info.value)


def test_github_repository_repo_blank():
    """
    Test GitHubRepository when the repo is blank.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='owner', repo='   ')
    assert (
        'repo\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='   ', input_type=str]\n"
    ) in str(exc_info.value)


def test_github_repository_repo_missing():
    """
    Test GitHubRepository when the repo is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='owner')
    assert (
        '1 validation error for GitHubRepository\nrepo\n  Field required ' +
        "[type=missing, input_value={'owner': 'owner'}, input_type=dict]"
    ) in str(exc_info.value)


def test_github_repository_get_file_extra():
    """
    Test GitHubRepository get_file when extra arguments are forbidden.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='owner', repo='repo').get_file(
            filename='filename', extra=1,
        )
    assert (
        'extra\n  Unexpected keyword argument ' +
        '[type=unexpected_keyword_argument, input_value=1, input_type=int]'
    ) in str(exc_info.value)


def test_github_repository_get_file_type():
    """
    Test GitHubRepository get_file when the filename type is not a string.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='owner', repo='repo').get_file(filename=1234.56)
    assert (
        'filename\n  Input should be a valid string [type=string_type, ' +
        'input_value=1234.56, input_type=float]'
    ) in str(exc_info.value)


def test_github_repository_get_file_empty():
    """
    Test GitHubRepository get_file when the filename is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='owner', repo='repo').get_file(filename='')
    assert (
        'filename\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='', input_type=str]\n"
    ) in str(exc_info.value)


def test_github_repository_get_file_blank():
    """
    Test GitHubRepository get_file when the filename is blank.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='owner', repo='repo').get_file(filename='   ')
    assert (
        'filename\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='   ', input_type=str]\n"
    ) in str(exc_info.value)


def test_github_repository_get_file_missing():
    """
    Test GitHubRepository get_file when the filename is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository(owner='owner', repo='repo').get_file()
    assert (
        'filename\n  Missing required argument [type=missing_argument, ' +
        "input_value=ArgsKwargs((GitHubReposit...'owner', repo='repo'),)), " +
        'input_type=ArgsKwargs]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_github_repository_get_file():
    """
    Test GitHubRepository get_file.

    Raises:
        AssertionError: If the test fails.
    """
    repository = GitHubRepository(owner='owner', repo='repo')
    assert repository.get_file('filename') == 'mock_content'


@pytest.mark.usefixtures('mock_urlopen_error')
def test_github_repository_get_file_unreachable():
    """
    Test GitHubRepository get_file when the URL is not reachable.

    Raises:
        AssertionError: If the test fails.
    """
    repository = GitHubRepository(owner='owner', repo='repo')
    with pytest.raises(ConnectionError) as exc_info:
        repository.get_file('filename')
    assert (
        'Failed to request ' +
        "'https://api.github.com/repos/owner/repo/contents/filename':\n" +
        '<urlopen error Mocked URLError>'
    ) in str(exc_info.value)


def test_github_repository_from_url_extra():
    """
    Test GitHubRepository from_url when extra arguments are forbidden.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository.from_url(
            'https://example.com/owner/repo.git', extra=1,
        )
    assert (
        'extra\n  Unexpected keyword argument ' +
        '[type=unexpected_keyword_argument, input_value=1, input_type=int]'
    ) in str(exc_info.value)


def test_github_repository_from_url():
    """
    Test GitHubRepository from_url.

    Raises:
        AssertionError: If the test fails.
    """
    repository = GitHubRepository.from_url(
        'https://example.com/owner/repo.git',
    )
    assert repository.owner == 'owner'
    assert repository.repo == 'repo'


def test_github_repository_from_url_parsing():
    """
    Test GitHubRepository from_url when the URL is not valid.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository.from_url('invalid-url')
    assert (
        '1\n  Input should be a valid URL, relative URL without a base ' +
        "[type=url_parsing, input_value='invalid-url', input_type=str]\n"
    ) in str(exc_info.value)


def test_github_repository_from_url_missing():
    """
    Test GitHubRepository from_url when the url is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        GitHubRepository.from_url()
    assert (
        'url\n  Missing required argument [type=missing_argument, ' +
        "input_value=ArgsKwargs((<class 'repos...ry.GitHubRepository'>,)), " +
        'input_type=ArgsKwargs]'
    ) in str(exc_info.value)


def test_github_repository_from_url_owner_error():
    """
    Test GitHubRepository from_url when the owner is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValueError) as exc_info:
        GitHubRepository.from_url('https://example.com')
    assert (
        "Failed to parse repository owner from 'https://example.com/':\n" +
        'list index out of range'
    ) in str(exc_info.value)


def test_github_repository_from_url_name_error():
    """
    Test GitHubRepository from_url when the name is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValueError) as exc_info:
        GitHubRepository.from_url('https://example.com/owner')
    assert (
        "Failed to parse repository name from 'https://example.com/owner':\n" +
        'list index out of range'
    ) in str(exc_info.value)


def test_repository_create_extra():
    """
    Test Repository create when extra arguments are forbidden.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Repository.create('https://example.com/owner/repo.git', extra=1)
    assert (
        'extra\n  Unexpected keyword argument ' +
        '[type=unexpected_keyword_argument, input_value=1, input_type=int]'
    ) in str(exc_info.value)


def test_repository_create_github():
    """
    Test Repository create GitHubRepository.

    Raises:
        AssertionError: If the test fails.
    """
    repository = Repository.create('https://github.com/owner/repo.git')
    assert isinstance(repository, GitHubRepository)


def test_repository_create_generic():
    """
    Test Repository create GenericRepository.

    Raises:
        AssertionError: If the test fails.
    """
    repository = Repository.create('https://generic.com/owner/repo.git')
    assert isinstance(repository, GenericRepository)


def test_repository_create_parsing():
    """
    Test Repository create when the URL is not valid.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Repository.create('invalid-url')
    assert (
        '1\n  Input should be a valid URL, relative URL without a base ' +
        "[type=url_parsing, input_value='invalid-url', input_type=str]\n"
    ) in str(exc_info.value)


def test_repository_create_missing():
    """
    Test Repository create when the URL is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Repository.create()
    assert (
        'url\n  Missing required argument [type=missing_argument, ' +
        "input_value=ArgsKwargs((<class 'repository.Repository'>,)), " +
        'input_type=ArgsKwargs]'
    ) in str(exc_info.value)


def test_repository_create_github_error():
    """
    Test Repository create when the GitHub repository is not valid.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValueError) as exc_info:
        Repository.create('https://github.com/owner')
    assert (
        "GitHub repository 'https://github.com/owner' is not valid:\nFailed " +
        "to parse repository name from 'https://github.com/owner':\nlist " +
        'index out of range'
    ) in str(exc_info.value)
