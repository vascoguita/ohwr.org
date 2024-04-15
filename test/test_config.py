# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Test pydantic_utils module."""

import io

import pytest
from config import (
    Category,
    CategoryList,
    Config,
    Contact,
    Project,
    ProjectList,
)
from pydantic import (
    BaseModel,
    DirectoryPath,
    FilePath,
    HttpUrl,
    ValidationError,
)
from pytest_utils import mock_urlopen, mock_urlopen_unreachable


def test_contact_extra():
    """
    Test Contact when extra attributes are forbidden.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Contact(name='Contact Name', email='valid@email.com', extra=1)
    assert (
        'extra\n  Extra inputs are not permitted ' +
        '[type=extra_forbidden, input_value=1, input_type=int]\n'
    ) in str(exc_info.value)


def test_contact_name():
    """
    Test Contact name.

    Raises:
        AssertionError: If the test fails.
    """
    contact = Contact(name='Contact Name', email='valid@email.com')
    assert contact.name == 'Contact Name'


def test_contact_name_type():
    """
    Test Contact name when the type is not a string.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Contact(name=1234.56, email='valid@email.com')
    assert (
        'name\n  Input should be a valid string ' +
        '[type=string_type, input_value=1234.56, input_type=float]\n'
    ) in str(exc_info.value)


def test_contact_name_empty():
    """
    Test Contact when the name is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Contact(name='', email='valid@email.com')
    assert (
        'name\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='', input_type=str]\n"
    ) in str(exc_info.value)


def test_contact_name_blank():
    """
    Test Contact when the name is blank.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Contact(name='   ', email='valid@email.com')
    assert (
        'name\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='   ', input_type=str]\n"
    ) in str(exc_info.value)


def test_contact_name_missing():
    """
    Test Contact when the name is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Contact(email='valid@email.com')
    assert (
        'name\n  Field required ' +
        "[type=missing, input_value={'email': 'valid@email.com'}, " +
        'input_type=dict]'
    ) in str(exc_info.value)


def test_contact_email():
    """
    Test Contact email.

    Raises:
        AssertionError: If the test fails.
    """
    contact = Contact(name='Contact Name', email='valid@email.com')
    assert contact.email == 'valid@email.com'


def test_contact_email_parsing():
    """
    Test Contact when the email is not valid.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Contact(name='Contact Name', email='invalid-email')
    assert (
        'email\n  value is not a valid email address: The email address is ' +
        'not valid. It must have exactly one @-sign. [type=value_error, ' +
        "input_value='invalid-email', input_type=str]"
    ) in str(exc_info.value)


def test_contact_email_missing():
    """
    Test Contact when the email is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Contact(email='valid@email.com')
    assert (
        'name\n  Field required ' +
        "[type=missing, input_value={'email': 'valid@email.com'}, " +
        'input_type=dict]'
    ) in str(exc_info.value)


def test_category_extra():
    """
    Test Category when extra attributes are forbidden.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Category(name='Category Name', description='Description', extra=1)
    assert (
        'extra\n  Extra inputs are not permitted ' +
        '[type=extra_forbidden, input_value=1, input_type=int]\n'
    ) in str(exc_info.value)


def test_category_name():
    """
    Test Category name.

    Raises:
        AssertionError: If the test fails.
    """
    category = Category(name='Category Name', description='Description')
    assert category.name == 'Category Name'


def test_category_name_type():
    """
    Test Category name when the type is not a string.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Category(name=1234.56, description='Description')
    assert (
        'name\n  Input should be a valid string ' +
        '[type=string_type, input_value=1234.56, input_type=float]\n'
    ) in str(exc_info.value)


def test_category_name_empty():
    """
    Test Category when the name is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Category(name='', description='Description')
    assert (
        'name\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='', input_type=str]\n"
    ) in str(exc_info.value)


def test_category_name_blank():
    """
    Test Category when the name is blank.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Category(name='   ', description='Description')
    assert (
        'name\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='   ', input_type=str]\n"
    ) in str(exc_info.value)


def test_category_name_missing():
    """
    Test Category when the name is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Category(description='Description')
    assert (
        'name\n  Field required ' +
        "[type=missing, input_value={'description': 'Description'}, " +
        'input_type=dict]'
    ) in str(exc_info.value)


def test_category_description():
    """
    Test Category description.

    Raises:
        AssertionError: If the test fails.
    """
    category = Category(name='Category Name', description='Description')
    assert category.description == 'Description'


def test_category_description_type():
    """
    Test Category description when the type is not a string.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Category(name='Category Name', description=1234.56)
    assert (
        'description\n  Input should be a valid string ' +
        '[type=string_type, input_value=1234.56, input_type=float]\n'
    ) in str(exc_info.value)


def test_category_description_empty():
    """
    Test Category when the description is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Category(name='Category Name', description='')
    assert (
        'description\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='', input_type=str]\n"
    ) in str(exc_info.value)


def test_category_description_blank():
    """
    Test Category when the description is blank.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Category(name='Category Name', description='  ')
    assert (
        'description\n  String should have at least 1 character ' +
        "[type=string_too_short, input_value='  ', input_type=str]\n"
    ) in str(exc_info.value)


def test_category_description_missing():
    """
    Test Category when the description is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Category(name='Category Name')
    assert (
        'description\n  Field required ' +
        "[type=missing, input_value={'name': 'Category Name'}, " +
        'input_type=dict]'
    ) in str(exc_info.value)


class CategoryListTest(BaseModel):
    """Test class for CategoryList."""

    test_attribute: CategoryList


def test_category_list():
    """
    Test case for CategoryList type.

    Raises:
        AssertionError: If the test fails.
    """
    test_object = CategoryListTest(test_attribute=[{
        'name': 'Category Name', 'description': 'Description',
    }])
    assert test_object.test_attribute == [
        Category(name='Category Name', description='Description'),
    ]


def test_category_list_type():
    """
    Test CategoryList when the type is not a list.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        CategoryListTest(test_attribute={
            'name': 'Category Name', 'description': 'Description',
        })
    assert (
        'test_attribute\n  Input should be a valid list ' +
        "[type=list_type, input_value={'name': 'Category Name',...ription': " +
        "'Description'}, input_type=dict]\n"
    ) in str(exc_info.value)


def test_category_list_empty():
    """
    Test CategoryList when the list is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        CategoryListTest(test_attribute=[])
    assert (
        'test_attribute\n  List should have at least 1 item after ' +
        'validation, not 0 [type=too_short, input_value=[], input_type=list]\n'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_project_extra():
    """
    Test Project when extra attributes are forbidden.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Project(
            repository='https://example.com/project.git',
            contact={'name': 'Contact Name', 'email': 'valid@email.com'},
            extra=1,
        )
    assert (
        'extra\n  Extra inputs are not permitted ' +
        '[type=extra_forbidden, input_value=1, input_type=int]\n'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_project_repository():
    """
    Test Project repository.

    Raises:
        AssertionError: If the test fails.
    """
    project = Project(
        repository='https://example.com/project.git',
        contact={'name': 'Contact Name', 'email': 'valid@email.com'},
    )
    assert project.repository == HttpUrl('https://example.com/project.git')


@pytest.mark.usefixtures('mock_urlopen')
def test_project_repository_parsing():
    """
    Test Project repository when the URL is not valid.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Project(
            repository='invalid-url',
            contact={'name': 'Contact Name', 'email': 'valid@email.com'},
        )
    assert (
        'repository\n  Input should be a valid URL, relative URL without' +
        " a base [type=url_parsing, input_value='invalid-url', " +
        'input_type=str]\n'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen_unreachable')
def test_project_repository_unreachable():
    """
    Test Project repository when the URL is not reachable.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Project(
            repository='https://unreachable.com',
            contact={'name': 'Contact Name', 'email': 'valid@email.com'},
        )
    assert (
        'repository\n  Value error, Failed to access URL: ' +
        "'https://unreachable.com/'. [type=value_error, " +
        "input_value='https://unreachable.com', input_type=str]\n"
    ) in str(exc_info.value)


def test_project_repository_missing():
    """
    Test Project when the repository is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Project(contact={'name': 'Contact Name', 'email': 'valid@email.com'})
    assert (
        'repository\n  Field required [type=missing, ' +
        "input_value={'contact': {'name': 'Con...il': 'valid@email.com'}}, " +
        'input_type=dict]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_project_contact():
    """
    Test Project contact.

    Raises:
        AssertionError: If the test fails.
    """
    project = Project(
        repository='https://example.com/project.git',
        contact={'name': 'Contact Name', 'email': 'valid@email.com'},
    )
    assert project.contact == Contact(
        name='Contact Name', email='valid@email.com',
    )


@pytest.mark.usefixtures('mock_urlopen')
def test_project_contact_parsing():
    """
    Test Project when the contact is not valid.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Project(
            repository='https://example.com/project.git',
            contact='invalid-contact',
        )
    assert (
        'contact\n  Input should be a valid dictionary or instance of ' +
        "Contact [type=model_type, input_value='invalid-contact', " +
        'input_type=str]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_project_contact_missing():
    """
    Test Project when the contact is missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Project(repository='https://example.com/project.git')
    assert (
        'contact\n  Field required [type=missing, ' +
        "input_value={'repository': 'https://example.com/project.git'}, " +
        'input_type=dict]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_project_featured():
    """
    Test Project featured.

    Raises:
        AssertionError: If the test fails.
    """
    project = Project(
        repository='https://example.com/project.git',
        contact={'name': 'Contact Name', 'email': 'valid@email.com'},
        featured=True,
    )
    assert project.featured is True


@pytest.mark.usefixtures('mock_urlopen')
def test_project_featured_default():
    """
    Test Project featured default value.

    Raises:
        AssertionError: If the test fails.
    """
    project = Project(
        repository='https://example.com/project.git',
        contact={'name': 'Contact Name', 'email': 'valid@email.com'},
    )
    assert project.featured is False


@pytest.mark.usefixtures('mock_urlopen')
def test_project_featured_type():
    """
    Test Project featured when the type is not a bool.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Project(
            repository='https://example.com/project.git',
            contact={'name': 'Contact Name', 'email': 'valid@email.com'},
            featured=1234.56,
        )
    assert (
        'featured\n  Input should be a valid boolean ' +
        '[type=bool_type, input_value=1234.56, input_type=float]\n'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_project_categories():
    """
    Test Project categories.

    Raises:
        AssertionError: If the test fails.
    """
    project = Project(
        repository='https://example.com/project.git',
        contact={'name': 'Contact Name', 'email': 'valid@email.com'},
        categories=['Category 1'],
    )
    assert project.categories == ['Category 1']


@pytest.mark.usefixtures('mock_urlopen')
def test_project_categories_type():
    """
    Test Project categories when the type is not a list.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Project(
            repository='https://example.com/project.git',
            contact={'name': 'Contact Name', 'email': 'valid@email.com'},
            categories=1234.56,
        )
    assert (
        'categories\n  Input should be a valid list ' +
        '[type=list_type, input_value=1234.56, input_type=float]\n'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_project_categories_empty():
    """
    Test Project categories when the list is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Project(
            repository='https://example.com/project.git',
            contact={'name': 'Contact Name', 'email': 'valid@email.com'},
            categories=[],
        )
    assert (
        'categories\n  List should have at least 1 item after validation, ' +
        'not 0 [type=too_short, input_value=[], input_type=list]\n'
    ) in str(exc_info.value)


class ProjectListTest(BaseModel):
    """Test class for CategoryList."""

    test_attribute: ProjectList


@pytest.mark.usefixtures('mock_urlopen')
def test_project_list():
    """
    Test case for ProjectList type.

    Raises:
        AssertionError: If the test fails.
    """
    test_object = ProjectListTest(test_attribute=[{
        'repository': 'https://example.com/project.git',
        'contact': {'name': 'Contact Name', 'email': 'valid@email.com'},
    }])
    assert test_object.test_attribute == [Project(
        repository='https://example.com/project.git',
        contact={'name': 'Contact Name', 'email': 'valid@email.com'},
    )]


@pytest.mark.usefixtures('mock_urlopen')
def test_project_list_type():
    """
    Test ProjectList when the type is not a list.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        ProjectListTest(test_attribute={
            'repository': 'https://example.com/project.git',
            'contact': {'name': 'Contact Name', 'email': 'valid@email.com'},
        })
    assert (
        'test_attribute\n  Input should be a valid list [type=list_type, ' +
        "input_value={'repository': 'https://e...il': 'valid@email.com'}}, " +
        'input_type=dict]'
    ) in str(exc_info.value)


def test_project_list_empty():
    """
    Test ProjectList when the list is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        ProjectListTest(test_attribute=[])
    assert (
        'test_attribute\n  List should have at least 1 item after ' +
        'validation, not 0 [type=too_short, input_value=[], input_type=list]\n'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_extra():
    """
    Test Config when extra attributes are forbidden.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./src/hugo',
            licenses='./third_party/spdx/license-list-data/json/licenses.json',
            projects=[{
                'repository': 'https://example.com/project.git',
                'contact': {
                    'name': 'Contact Name', 'email': 'valid@email.com',
                },
            }],
            extra=1,
        )
    assert (
        'extra\n  Extra inputs are not permitted ' +
        '[type=extra_forbidden, input_value=1, input_type=int]\n'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_sources():
    """
    Test Config sources.

    Raises:
        AssertionError: If the test fails.
    """
    config = Config(
        sources='./src/hugo',
        licenses='./third_party/spdx/license-list-data/json/licenses.json',
        projects=[{
            'repository': 'https://example.com/project.git',
            'contact': {
                'name': 'Contact Name', 'email': 'valid@email.com',
            },
        }],
    )
    assert config.sources == DirectoryPath('./src/hugo')


@pytest.mark.usefixtures('mock_urlopen')
def test_config_sources_type():
    """
    Test Config sources when the type is not a DirectoryPath.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources=1234.56,
            licenses='./third_party/spdx/license-list-data/json/licenses.json',
            projects=[{
                'repository': 'https://example.com/project.git',
                'contact': {
                    'name': 'Contact Name', 'email': 'valid@email.com',
                },
            }],
        )
    assert (
        'sources\n  Input is not a valid path ' +
        '[type=path_type, input_value=1234.56, input_type=float]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_sources_non_existent():
    """
    Test Config when the sources directory does not exist.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./non/existent/directory',
            licenses='./third_party/spdx/license-list-data/json/licenses.json',
            projects=[{
                'repository': 'https://example.com/project.git',
                'contact': {
                    'name': 'Contact Name', 'email': 'valid@email.com',
                },
            }],
        )
    assert (
        'sources\n  Path does not point to a directory ' +
        "[type=path_not_directory, input_value='./non/existent/directory', " +
        'input_type=str]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_sources_missing():
    """
    Test Config when the sources are missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            licenses='./third_party/spdx/license-list-data/json/licenses.json',
            projects=[{
                'repository': 'https://example.com/project.git',
                'contact': {
                    'name': 'Contact Name', 'email': 'valid@email.com',
                },
            }],
        )
    assert (
        'sources\n  Field required [type=missing, ' +
        "input_value={'licenses': './third_par...': 'valid@email.com'}}]}, " +
        'input_type=dict]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_licenses():
    """
    Test Config licenses.

    Raises:
        AssertionError: If the test fails.
    """
    config = Config(
        sources='./src/hugo',
        licenses='./third_party/spdx/license-list-data/json/licenses.json',
        projects=[{
            'repository': 'https://example.com/project.git',
            'contact': {
                'name': 'Contact Name', 'email': 'valid@email.com',
            },
        }],
    )
    assert config.licenses == FilePath(
        './third_party/spdx/license-list-data/json/licenses.json',
    )


@pytest.mark.usefixtures('mock_urlopen')
def test_config_licenses_type():
    """
    Test Config licenses when the type is not a string.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./src/hugo',
            licenses=1234.56,
            projects=[{
                'repository': 'https://example.com/project.git',
                'contact': {
                    'name': 'Contact Name', 'email': 'valid@email.com',
                },
            }],
        )
    assert (
        'licenses\n  Input is not a valid path [type=path_type, ' +
        'input_value=1234.56, input_type=float]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_licenses_non_existent():
    """
    Test Config when the licenses file does not exist.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./src/hugo',
            licenses='./non/existent/file',
            projects=[{
                'repository': 'https://example.com/project.git',
                'contact': {
                    'name': 'Contact Name', 'email': 'valid@email.com',
                },
            }],
        )
    assert (
        'licenses\n  Path does not point to a file [type=path_not_file, ' +
        "input_value='./non/existent/file', input_type=str]"
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_licenses_missing():
    """
    Test Config when the licenses are missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./src/hugo',
            projects=[{
                'repository': 'https://example.com/project.git',
                'contact': {
                    'name': 'Contact Name', 'email': 'valid@email.com',
                },
            }],
        )
    assert (
        'licenses\n  Field required [type=missing, ' +
        "input_value={'sources': './src/hugo',...': 'valid@email.com'}}]}, " +
        'input_type=dict]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_projects():
    """
    Test Config projects.

    Raises:
        AssertionError: If the test fails.
    """
    config = Config(
        sources='./src/hugo',
        licenses='./third_party/spdx/license-list-data/json/licenses.json',
        projects=[{
            'repository': 'https://example.com/project.git',
            'contact': {
                'name': 'Contact Name', 'email': 'valid@email.com',
            },
        }],
    )
    assert config.projects == [Project(
        repository='https://example.com/project.git',
        contact={'name': 'Contact Name', 'email': 'valid@email.com'},
    )]


@pytest.mark.usefixtures('mock_urlopen')
def test_config_projects_type():
    """
    Test Config projects when the type is not a list.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./src/hugo',
            licenses='./third_party/spdx/license-list-data/json/licenses.json',
            projects=1234.56,
        )
    assert (
        'projects\n  Input should be a valid list ' +
        '[type=list_type, input_value=1234.56, input_type=float]\n'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_projects_empty():
    """
    Test Config projects when the list is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./src/hugo',
            licenses='./third_party/spdx/license-list-data/json/licenses.json',
            projects=[],
        )
    assert (
        'projects\n  List should have at least 1 item after validation, ' +
        'not 0 [type=too_short, input_value=[], input_type=list]\n'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_projects_missing():
    """
    Test Config when the projects are missing.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./src/hugo',
            licenses='./third_party/spdx/license-list-data/json/licenses.json',
        )
    assert (
        'projects\n  Field required [type=missing, ' +
        "input_value={'sources': './src/hugo',...ata/json/licenses.json'}, " +
        'input_type=dict]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_log_level():
    """
    Test Config log_level.

    Raises:
        AssertionError: If the test fails.
    """
    config = Config(
        sources='./src/hugo',
        licenses='./third_party/spdx/license-list-data/json/licenses.json',
        log_level='DEBUG',
        projects=[{
            'repository': 'https://example.com/project.git',
            'contact': {
                'name': 'Contact Name', 'email': 'valid@email.com',
            },
        }],
    )
    assert config.log_level == 'DEBUG'


@pytest.mark.usefixtures('mock_urlopen')
def test_config_log_level_literal():
    """
    Test Config log_level when the value is not one of the valid literals.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./src/hugo',
            licenses='./third_party/spdx/license-list-data/json/licenses.json',
            log_level='WRONG',
            projects=[{
                'repository': 'https://example.com/project.git',
                'contact': {
                    'name': 'Contact Name', 'email': 'valid@email.com',
                },
            }],
        )
    assert (
        "log_level\n  Input should be 'DEBUG', 'INFO', 'WARNING', 'ERROR' " +
        "or 'CRITICAL' [type=literal_error, input_value='WRONG', " +
        'input_type=str]'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_categories():
    """
    Test Config categories.

    Raises:
        AssertionError: If the test fails.
    """
    config = Config(
        sources='./src/hugo',
        licenses='./third_party/spdx/license-list-data/json/licenses.json',
        categories=[{'name': 'Category Name', 'description': 'Description'}],
        projects=[{
            'repository': 'https://example.com/project.git',
            'contact': {
                'name': 'Contact Name', 'email': 'valid@email.com',
            },
        }],
    )
    assert config.categories == [
        Category(name='Category Name', description='Description'),
    ]


@pytest.mark.usefixtures('mock_urlopen')
def test_config_categories_type():
    """
    Test Config categories when the type is not a list.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./src/hugo',
            licenses='./third_party/spdx/license-list-data/json/licenses.json',
            categories=1234.56,
            projects=[{
                'repository': 'https://example.com/project.git',
                'contact': {
                    'name': 'Contact Name', 'email': 'valid@email.com',
                },
            }],
        )
    assert (
        'categories\n  Input should be a valid list ' +
        '[type=list_type, input_value=1234.56, input_type=float]\n'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_categories_empty():
    """
    Test Config categories when the list is empty.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./src/hugo',
            licenses='./third_party/spdx/license-list-data/json/licenses.json',
            categories=[],
            projects=[{
                'repository': 'https://example.com/project.git',
                'contact': {
                    'name': 'Contact Name', 'email': 'valid@email.com',
                },
            }],
        )
    assert (
        'categories\n  List should have at least 1 item after validation, ' +
        'not 0 [type=too_short, input_value=[], input_type=list]\n'
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_categories_match():
    """
    Test Config categories match Project categories.

    Raises:
        AssertionError: If the test fails.
    """
    config = Config(
        sources='./src/hugo',
        licenses='./third_party/spdx/license-list-data/json/licenses.json',
        categories=[{'name': 'Category Name', 'description': 'Description'}],
        projects=[{
            'repository': 'https://example.com/project.git',
            'contact': {
                'name': 'Contact Name', 'email': 'valid@email.com',
            },
            'categories': ['Category Name'],
        }],
    )
    assert config.projects[0].categories[0] == config.categories[0].name


@pytest.mark.usefixtures('mock_urlopen')
def test_config_categories_no_match():
    """
    Test Config categories when Project categories do not match.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValidationError) as exc_info:
        Config(
            sources='./src/hugo',
            licenses='./third_party/spdx/license-list-data/json/licenses.json',
            categories=[
                {'name': 'Category Name', 'description': 'Description'},
            ],
            projects=[{
                'repository': 'https://example.com/project.git',
                'contact': {
                    'name': 'Contact Name', 'email': 'valid@email.com',
                },
                'categories': ['Wrong Name'],
            }],
        )
    assert (
        "Project 'https://example.com/project.git' with unknown categories: " +
        "'{'Wrong Name'}'. [type=value_error, input_value={'sources': " +
        "'./src/hugo',...ries': ['Wrong Name']}]}, input_type=dict]"
    ) in str(exc_info.value)


@pytest.mark.usefixtures('mock_urlopen')
def test_config_from_yaml():
    """
    Test Config from YAML.

    Raises:
        AssertionError: If the test fails.
    """
    config_yaml = """
---
# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

sources: './src/hugo'
licenses: './third_party/spdx/license-list-data/json/licenses.json'
projects:
- repository: 'https://example.com/project.git'
  contact:
    name: 'Contact Name'
    email: 'valid@email.com'
"""
    config = Config.from_yaml(io.StringIO(config_yaml))
    assert config == Config(
        sources='./src/hugo',
        licenses='./third_party/spdx/license-list-data/json/licenses.json',
        projects=[{
            'repository': 'https://example.com/project.git',
            'contact': {
                'name': 'Contact Name', 'email': 'valid@email.com',
            },
        }],
    )


def test_config_from_yaml_parsing():
    """
    Test Config from YAML when the YAML is not valid.

    Raises:
        AssertionError: If the test fails.
    """
    with pytest.raises(ValueError) as exc_info:
        Config.from_yaml('unbalanced blackets: ][')
    assert (
        'Failed to load YAML configuration:\nwhile parsing a block node\n' +
        "expected the node content, but found ']'"
    ) in str(exc_info.value)


def test_config_from_yaml_valid():
    """
    Test Config from YAML when the Config is not valid.

    Raises:
        AssertionError: If the test fails.
    """
    config_yaml = """
---
# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

sources: './src/hugo'
licenses: './third_party/spdx/license-list-data/json/licenses.json'
"""
    with pytest.raises(ValueError) as exc_info:
        Config.from_yaml(config_yaml)
    assert (
        'YAML configuration is not valid:\n1 validation error for ' +
        'Config\nprojects\n  Field required [type=missing, ' +
        "input_value={'sources': './src/hugo',...ata/json/licenses.json'}, " +
        'input_type=dict]'
    ) in str(exc_info.value)
