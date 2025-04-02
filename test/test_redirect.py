# SPDX-FileCopyrightText: 2024
#
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for redirect module."""

import pytest

from config import Redirect
from redirect import RedirectPage, RedirectSection


OS_MAKEDIRS = "os.makedirs"


@pytest.fixture(autouse=True)
def mock_requests(mocker):
    """Mock requests.head to avoid real HTTP calls."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_head = mocker.patch('requests.head', return_value=mock_response)
    return mock_head


@pytest.fixture
def sample_redirect_config():
    """Return a sample Redirect configuration."""
    return Redirect(source="old/path", target="https://example.com/new/path")


@pytest.fixture
def sample_redirect_configs():
    """Return a list of sample Redirect configurations."""
    return [
        Redirect(source="old/path1", target="https://example.com/new/path1"),
        Redirect(source="old/path2", target="https://example.com/new/path2"),
        Redirect(source="old/path3", target="https://example.com/new/path3"),
    ]


class TestRedirectPage:
    """Tests for RedirectPage class."""

    def test_from_config(self, sample_redirect_config):
        """Test creating a RedirectPage from config."""
        page = RedirectPage.from_config(sample_redirect_config)

        assert page.front_matter["type"] == "redirect"
        assert page.front_matter["target"] == "https://example.com/new/path"
        assert page.markdown == ""

    def test_from_config_minimal(self, mock_requests):
        """Test creating a RedirectPage with minimal config."""
        config = Redirect(source="minimal", target="https://example.com/path")
        page = RedirectPage.from_config(config)

        assert page.front_matter["type"] == "redirect"
        assert page.front_matter["target"] == "https://example.com/path"
        assert page.markdown == ""
        mock_requests.assert_called_once_with(
            "https://example.com/path",
            allow_redirects=True,
            timeout=10
        )


class MockFromConfigHelper:
    def __init__(self, invalid_config, original_from_config):
        self.invalid_config = invalid_config
        self.original_from_config = original_from_config

    def __call__(self, config):
        if config == self.invalid_config:
            raise ValueError("Test error")
        return self.original_from_config(config)


class TestRedirectSection:
    """Tests for RedirectSection class."""

    def test_from_config(self, sample_redirect_configs, mock_requests):
        """Test creating a RedirectSection from configs."""
        section = RedirectSection.from_config(sample_redirect_configs)
        sample_redirect_configs_length = len(sample_redirect_configs)

        assert len(section) == sample_redirect_configs_length
        for config in sample_redirect_configs:
            assert config.source in section
            assert isinstance(section[config.source], RedirectPage)
        assert mock_requests.call_count == sample_redirect_configs_length

    def test_from_config_with_invalid_config(
        self, sample_redirect_configs, caplog, mocker, mock_requests
    ):
        """Test creating a RedirectSection with one invalid config."""
        invalid_config = Redirect(
            source="invalid",
            target="https://example.com/not-found",
        )
        configs = sample_redirect_configs + [invalid_config]

        original_from_config = RedirectPage.from_config

        helper = MockFromConfigHelper(invalid_config, original_from_config)
        mocker.patch.object(
            RedirectPage, 'from_config',
            side_effect=helper,
        )
        section = RedirectSection.from_config(configs)

        assert len(section) == len(sample_redirect_configs)
        assert "Failed to generate 'invalid' page" in caplog.text

    def test_page_path_success(self, mocker):
        """Test _page_path method with successful directory creation."""
        section = RedirectSection({})
        mock_makedirs = mocker.patch(OS_MAKEDIRS)

        res = section._page_path("/base/path", "page_name")

        assert res == "/base/path/page_name/index.md"
        mock_makedirs.assert_called_once_with("/base/path/page_name")

    def test_page_path_existing_dir(self, mocker):
        """Test _page_path with existing directory (should still succeed)."""
        section = RedirectSection({})
        mock_makedirs = mocker.patch(OS_MAKEDIRS)

        res = section._page_path("/base/path", "existing_dir")

        assert res == "/base/path/existing_dir/index.md"
        mock_makedirs.assert_called_once_with("/base/path/existing_dir")

    def test_page_path_creation_failure(self, mocker):
        """Test _page_path when directory creation fails."""
        section = RedirectSection({})
        mocker.patch(OS_MAKEDIRS, side_effect=OSError("Test error"))

        with pytest.raises(ValueError) as excinfo:
            section._page_path("/base/path", "invalid_dir")

        assert "Failed to create '/base/path/invalid_dir' directory" in str(
            excinfo.value
        )

    def test_write_success(
        self, sample_redirect_configs, mocker, mock_requests
    ):
        """Test successful write operation with mocked file operations."""
        mock_makedirs = mocker.patch(OS_MAKEDIRS)
        mock_open = mocker.patch('builtins.open', mocker.mock_open())
        sample_redirect_configs_length = len(sample_redirect_configs)

        RedirectSection.from_config(sample_redirect_configs).write(
            "/output/path"
        )

        assert mock_makedirs.call_count == sample_redirect_configs_length
        assert mock_open.call_count == sample_redirect_configs_length
        assert mock_requests.call_count == sample_redirect_configs_length

        for call in mock_makedirs.call_args_list:
            args, _ = call
            assert args[0].startswith("/output/path/")

    def test_write_failure(
        self, sample_redirect_configs, mocker, caplog, mock_requests
    ):
        """Test write operation with file write failure."""
        section = RedirectSection.from_config(sample_redirect_configs)
        mock_makedirs = mocker.patch(OS_MAKEDIRS)
        mock_open = mocker.patch(
            'builtins.open', side_effect=OSError("Test error")
        )
        sample_redirect_configs_length = len(sample_redirect_configs)

        section.write("/output/path")

        assert "Failed to write" in caplog.text
        assert mock_makedirs.call_count == sample_redirect_configs_length
        assert mock_open.call_count == sample_redirect_configs_length
        assert mock_requests.call_count == sample_redirect_configs_length
