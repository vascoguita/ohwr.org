# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Test config module."""

from http import HTTPStatus
from unittest.mock import Mock, patch
from urllib import request
from urllib.error import URLError

import pytest
from config import ExtProjConfig, LinkConfig
from pydantic import HttpUrl, ValidationError
from custom_types import License

License.config({'licenses': [{'licenseId': 'CERN-OHL-W-2.0'}]})

def test_link_config_extra_forbidden():
    with pytest.raises(ValidationError) as exc_info:
        LinkConfig(
            peanut=1,
            name='Link Name',
            url='https://your.project.com/link',
        )

    error_message = (
        "peanut\n"
        "  Extra inputs are not permitted [type=extra_forbidden, input_value=1, input_type=int]\n"
    )

    assert error_message in str(exc_info.value)

def test_link_config_name():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = LinkConfig(
            name='Link Name',
            url='https://your.project.com/link',
        )

        assert config.name == 'Link Name'

def test_link_config_name_string_type():
    with pytest.raises(ValidationError) as exc_info:
        LinkConfig(
            name=1234.56,
            url='https://your.project.com/link',
        )

    error_message = (
        "name\n"
        "  Input should be a valid string [type=string_type, input_value=1234.56, input_type=float]\n"
    )

    assert error_message in str(exc_info.value)

def test_link_config_name_empty():
    with pytest.raises(ValidationError) as exc_info:
        LinkConfig(
            name='',
            url='https://your.project.com/link',
        )
    
    error_message = (
        "name\n"
        "  String should have at least 1 character [type=string_too_short, input_value='', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_link_config_name_blank():
    with pytest.raises(ValidationError) as exc_info:
        LinkConfig(
            name='   ',
            url='https://your.project.com/link',
        )
    
    error_message = (
        "name\n"
        "  String should have at least 1 character [type=string_too_short, input_value='   ', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_link_config_name_missing():
    with pytest.raises(ValidationError) as exc_info:
        LinkConfig(
            url='https://your.project.com/link',
        )

    error_message = (
        "name\n"
        "  Field required [type=missing, input_value={'url': 'https://your.project.com/link'}, input_type=dict]\n"
    )

    assert error_message in str(exc_info.value)

def test_link_config_url():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = LinkConfig(
            name='Link Name',
            url='https://your.project.com/link',
        )

        assert config.url == HttpUrl('https://your.project.com/link')

def test_link_config_url_url_parsing():
    with pytest.raises(ValidationError) as exc_info:
        LinkConfig(
            name='Link Name',
            url='invalid-url',
        )

    error_message = (
        "url\n"
        "  Input should be a valid URL, relative URL without a base [type=url_parsing, input_value='invalid-url', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_link_config_url_missing():
    with pytest.raises(ValidationError) as exc_info:
        LinkConfig(
            name='Link Name',
        )

    error_message = (
        "url\n"
        "  Field required [type=missing, input_value={'name': 'Link Name'}, input_type=dict]\n"
    )

    assert error_message in str(exc_info.value)

def test_link_config_url_unreachable():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_urlopen.side_effect = URLError("Mocked URLError")

        with pytest.raises(ValueError) as exc_info:
            LinkConfig(
                name='Link Name',
                url='https://unreachable.url',
            )
        
        error_message = (
            "url\n"
            "  Value error, Failed to access URL: 'https://unreachable.url/'. [type=value_error, input_value='https://unreachable.url', input_type=str]\n"
        )

        assert error_message in str(exc_info.value)

def test_proj_config_extra_forbidden():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            peanut=1,
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

    error_message = (
        "peanut\n"
        "  Extra inputs are not permitted [type=extra_forbidden, input_value=1, input_type=int]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_version():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

        assert config.version == '1.0.0'

def test_proj_config_version_literal_error():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.2.3',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

    error_message = (
        "version\n"
        "  Input should be '1.0.0' [type=literal_error, input_value='1.2.3', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_version_missing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

    error_message = (
        "version\n"
        "  Field required [type=missing, input_value={'name': 'Project Name', ...es': ['CERN-OHL-W-2.0']}, input_type=dict]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_name():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

        assert config.name == 'Project Name'

def test_proj_config_name_string_type():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name=1234.56,
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

    error_message = (
        "name\n"
        "  Input should be a valid string [type=string_type, input_value=1234.56, input_type=float]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_name_empty():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )
    
    error_message = (
        "name\n"
        "  String should have at least 1 character [type=string_too_short, input_value='', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_name_blank():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='   ',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )
    
    error_message = (
        "name\n"
        "  String should have at least 1 character [type=string_too_short, input_value='   ', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_name_missing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

    error_message = (
        "name\n"
        "  Field required [type=missing, input_value={'version': '1.0.0', 'des...es': ['CERN-OHL-W-2.0']}, input_type=dict]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_description():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

        assert config.description == 'Lorem ipsum dolor sit amet.'

def test_proj_config_description_string_type():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description=1234.56,
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

    error_message = (
        "description\n"
        "  Input should be a valid string [type=string_type, input_value=1234.56, input_type=float]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_description_empty():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )
    
    error_message = (
        "description\n"
        "  String should have at least 1 character [type=string_too_short, input_value='', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_description_blank():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='   ',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )
    
    error_message = (
        "description\n"
        "  String should have at least 1 character [type=string_too_short, input_value='   ', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_description_missing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

    error_message = (
        "description\n"
        "  Field required [type=missing, input_value={'version': '1.0.0', 'nam...es': ['CERN-OHL-W-2.0']}, input_type=dict]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_website():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

        assert config.website == HttpUrl('https://your.project.com')

def test_proj_config_website_url_parsing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='invalid-url',
            licenses=['CERN-OHL-W-2.0'],
        )

    error_message = (
        "website\n"
        "  Input should be a valid URL, relative URL without a base [type=url_parsing, input_value='invalid-url', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_website_missing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            licenses=['CERN-OHL-W-2.0'],
        )

    error_message = (
        "website\n"
        "  Field required [type=missing, input_value={'version': '1.0.0', 'nam...es': ['CERN-OHL-W-2.0']}, input_type=dict]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_website_unreachable():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_urlopen.side_effect = URLError("Mocked URLError")

        with pytest.raises(ValueError) as exc_info:
            ExtProjConfig(
                version='1.0.0',
                name='Project Name',
                description='Lorem ipsum dolor sit amet.',
                website='https://unreachable.url',
                licenses=['CERN-OHL-W-2.0'],
            )
        
        error_message = (
            "website\n"
            "  Value error, Failed to access URL: 'https://unreachable.url/'. [type=value_error, input_value='https://unreachable.url', input_type=str]\n"
        )

        assert error_message in str(exc_info.value)

def test_proj_config_licenses():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
        )

        assert config.licenses == ['CERN-OHL-W-2.0']

def test_proj_config_licenses_list_type():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses='abcd'
        )

    error_message = (
        "licenses\n"
        "  Input should be a valid list [type=list_type, input_value='abcd', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_licenses_empty():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=[],
        )
    
    error_message = (
        "licenses\n"
        "  List should have at least 1 item after validation, not 0 [type=too_short, input_value=[], input_type=list]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_licenses_empty_string():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=[''],
        )
    
    error_message = (
        "licenses.0\n"
        "  String should have at least 1 character [type=string_too_short, input_value='', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_licenses_blank_string():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['   '],
        )
    
    error_message = (
        "licenses.0\n"
        "  String should have at least 1 character [type=string_too_short, input_value='   ', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_licenses_missing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
        )

    error_message = (
        "licenses\n"
        "  Field required [type=missing, input_value={'version': '1.0.0', 'nam...tps://your.project.com'}, input_type=dict]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_licenses_not_spdx():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['NO-SPDX-LICENSE-ID'],
        )
    
    error_message = (
        "licenses.0\n"
        "  Value error, Unknown SPDX license identifier: 'NO-SPDX-LICENSE-ID'. [type=value_error, input_value='NO-SPDX-LICENSE-ID', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_images():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            images=['https://your.project.com/img.png'],
        )

        assert config.images == [HttpUrl('https://your.project.com/img.png')]

def test_proj_config_images_list_type():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            images='abcd',
        )

    error_message = (
        "images\n"
        "  Input should be a valid list [type=list_type, input_value='abcd', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_images_empty():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            images=[]
        )
    
    error_message = (
        "images\n"
        "  List should have at least 1 item after validation, not 0 [type=too_short, input_value=[], input_type=list]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_images_url_parsing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            images=['invalid-url']
        )

    error_message = (
        "images.0\n"
        "  Input should be a valid URL, relative URL without a base [type=url_parsing, input_value='invalid-url', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_images_unreachable():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_urlopen.side_effect = URLError("Mocked URLError")

        with pytest.raises(ValueError) as exc_info:
            ExtProjConfig(
                version='1.0.0',
                name='Project Name',
                description='Lorem ipsum dolor sit amet.',
                website='https://your.project.com',
                licenses=['CERN-OHL-W-2.0'],
                images=['https://unreachable.url'],
            )
        
        error_message = (
            "images.0\n"
            "  Value error, Failed to access URL: 'https://unreachable.url/'. [type=value_error, input_value='https://unreachable.url', input_type=str]\n"
        )

        assert error_message in str(exc_info.value)

def test_proj_config_documentation():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            documentation='https://your.project.com/wiki',
        )

        assert config.documentation == HttpUrl('https://your.project.com/wiki')

def test_proj_config_documentation_url_parsing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            documentation='invalid-url',
        )

    error_message = (
        "documentation\n"
        "  Input should be a valid URL, relative URL without a base [type=url_parsing, input_value='invalid-url', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_documentation_unreachable():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_urlopen.side_effect = URLError("Mocked URLError")

        with pytest.raises(ValueError) as exc_info:
            ExtProjConfig(
                version='1.0.0',
                name='Project Name',
                description='Lorem ipsum dolor sit amet.',
                website='https://your.project.com',
                licenses=['CERN-OHL-W-2.0'],
                documentation='https://unreachable.url',
            )
        
        error_message = (
            "documentation\n"
            "  Value error, Failed to access URL: 'https://unreachable.url/'. [type=value_error, input_value='https://unreachable.url', input_type=str]\n"
        )

        assert error_message in str(exc_info.value)

def test_proj_config_issues():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            issues='https://your.project.com/issues',
        )

        assert config.issues == HttpUrl('https://your.project.com/issues')

def test_proj_config_issues_url_parsing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            issues='invalid-url',
        )

    error_message = (
        "issues\n"
        "  Input should be a valid URL, relative URL without a base [type=url_parsing, input_value='invalid-url', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_issues_unreachable():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_urlopen.side_effect = URLError("Mocked URLError")

        with pytest.raises(ValueError) as exc_info:
            ExtProjConfig(
                version='1.0.0',
                name='Project Name',
                description='Lorem ipsum dolor sit amet.',
                website='https://your.project.com',
                licenses=['CERN-OHL-W-2.0'],
                issues='https://unreachable.url',
            )
        
        error_message = (
            "issues\n"
            "  Value error, Failed to access URL: 'https://unreachable.url/'. [type=value_error, input_value='https://unreachable.url', input_type=str]\n"
        )

        assert error_message in str(exc_info.value)

def test_proj_config_latest_release():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            latest_release='https://your.project.com/latest_release',
        )

        assert config.latest_release == HttpUrl('https://your.project.com/latest_release')

def test_proj_config_latest_release_url_parsing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            latest_release='invalid-url',
        )

    error_message = (
        "latest_release\n"
        "  Input should be a valid URL, relative URL without a base [type=url_parsing, input_value='invalid-url', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_latest_release_unreachable():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_urlopen.side_effect = URLError("Mocked URLError")

        with pytest.raises(ValueError) as exc_info:
            ExtProjConfig(
                version='1.0.0',
                name='Project Name',
                description='Lorem ipsum dolor sit amet.',
                website='https://your.project.com',
                licenses=['CERN-OHL-W-2.0'],
                latest_release='https://unreachable.url',
            )
        
        error_message = (
            "latest_release\n"
            "  Value error, Failed to access URL: 'https://unreachable.url/'. [type=value_error, input_value='https://unreachable.url', input_type=str]\n"
        )

        assert error_message in str(exc_info.value)

def test_proj_config_forum():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            forum='https://your.project.com/forum',
        )

        assert config.forum == HttpUrl('https://your.project.com/forum')

def test_proj_config_forum_url_parsing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            forum='invalid-url',
        )

    error_message = (
        "forum\n"
        "  Input should be a valid URL, relative URL without a base [type=url_parsing, input_value='invalid-url', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_forum_unreachable():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_urlopen.side_effect = URLError("Mocked URLError")

        with pytest.raises(ValueError) as exc_info:
            ExtProjConfig(
                version='1.0.0',
                name='Project Name',
                description='Lorem ipsum dolor sit amet.',
                website='https://your.project.com',
                licenses=['CERN-OHL-W-2.0'],
                forum='https://unreachable.url',
            )
        
        error_message = (
            "forum\n"
            "  Value error, Failed to access URL: 'https://unreachable.url/'. [type=value_error, input_value='https://unreachable.url', input_type=str]\n"
        )

        assert error_message in str(exc_info.value)

def test_proj_config_newsfeed():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            newsfeed='https://your.project.com/newsfeed',
        )

        assert config.newsfeed == HttpUrl('https://your.project.com/newsfeed')

def test_proj_config_newsfeed_url_parsing():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            newsfeed='invalid-url',
        )

    error_message = (
        "newsfeed\n"
        "  Input should be a valid URL, relative URL without a base [type=url_parsing, input_value='invalid-url', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_newsfeed_unreachable():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_urlopen.side_effect = URLError("Mocked URLError")

        with pytest.raises(ValueError) as exc_info:
            ExtProjConfig(
                version='1.0.0',
                name='Project Name',
                description='Lorem ipsum dolor sit amet.',
                website='https://your.project.com',
                licenses=['CERN-OHL-W-2.0'],
                newsfeed='https://unreachable.url',
            )
        
        error_message = (
            "newsfeed\n"
            "  Value error, Failed to access URL: 'https://unreachable.url/'. [type=value_error, input_value='https://unreachable.url', input_type=str]\n"
        )

        assert error_message in str(exc_info.value)

def test_proj_config_links():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            links=[{'name' : 'Link 1', 'url' : 'https://your.project.com/link1'}]
        )

        assert config.links == [LinkConfig(name='Link 1', url='https://your.project.com/link1')]

def test_proj_config_links_list_type():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            links='abcd',
        )

    error_message = (
        "links\n"
        "  Input should be a valid list [type=list_type, input_value='abcd', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_links_empty():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            links=[]
        )
    
    error_message = (
        "links\n"
        "  List should have at least 1 item after validation, not 0 [type=too_short, input_value=[], input_type=list]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_links_model_type():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            links=['invalid-link'],
        )

    error_message = (
        "links.0\n"
        "  Input should be a valid dictionary or instance of LinkConfig [type=model_type, input_value='invalid-link', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_links_unreachable():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_urlopen.side_effect = URLError("Mocked URLError")

        with pytest.raises(ValueError) as exc_info:
            ExtProjConfig(
                version='1.0.0',
                name='Project Name',
                description='Lorem ipsum dolor sit amet.',
                website='https://your.project.com',
                licenses=['CERN-OHL-W-2.0'],
                links=[{'name' : 'Link 1', 'url' : 'https://unreachable.url'}],
            )
        
        error_message = (
            "links.0.url\n"
            "  Value error, Failed to access URL: 'https://unreachable.url/'. [type=value_error, input_value='https://unreachable.url', input_type=str]\n"
        )

        assert error_message in str(exc_info.value)

def test_proj_config_categories():
    with patch.object(request, 'urlopen') as mock_urlopen:
        mock_response = Mock()
        mock_response.status = HTTPStatus.OK
        mock_urlopen.return_value.__enter__.return_value = mock_response

        config = ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            categories=['Category 1'],
        )

        assert config.categories == ['Category 1']

def test_proj_config_categories_list_type():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            categories='abcd'
        )

    error_message = (
        "categories\n"
        "  Input should be a valid list [type=list_type, input_value='abcd', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_categories_empty():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            categories=[],
        )
    
    error_message = (
        "categories\n"
        "  List should have at least 1 item after validation, not 0 [type=too_short, input_value=[], input_type=list]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_categories_empty_string():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            categories=[''],
        )
    
    error_message = (
        "categories.0\n"
        "  String should have at least 1 character [type=string_too_short, input_value='', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)

def test_proj_config_categories_blank_string():
    with pytest.raises(ValidationError) as exc_info:
        ExtProjConfig(
            version='1.0.0',
            name='Project Name',
            description='Lorem ipsum dolor sit amet.',
            website='https://your.project.com',
            licenses=['CERN-OHL-W-2.0'],
            categories=['   '],
        )
    
    error_message = (
        "categories.0\n"
        "  String should have at least 1 character [type=string_too_short, input_value='   ', input_type=str]\n"
    )

    assert error_message in str(exc_info.value)
