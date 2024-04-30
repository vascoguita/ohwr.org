# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load news."""

import datetime
import os
import re
from urllib import request
from urllib.error import URLError

import yaml
from pydantic import (
    DirectoryPath,
    HttpUrl,
    TypeAdapter,
    ValidationError,
    computed_field,
    validate_call,
)
from pydantic_utils import (
    AnnotatedStr,
    AnnotatedStrList,
    BaseModelForbidExtra,
    ReachableUrlList,
)


class News(BaseModelForbidExtra):
    """Project news."""

    newsfeed: AnnotatedStrList
    md: AnnotatedStr

    @computed_field
    def title(self) -> str:
        """
        Get title from Markdown.

        Returns:
            str: title.

        Raises:
            ValueError: If the title cannot be parsed from the Markdown.
        """
        try:
            return re.search('^## (.+)', self.md).group(1).strip()
        except (re.error, TypeError, IndexError) as title_error:
            raise ValueError('Failed to parse title:\n{0}'.format(title_error))

    @computed_field
    def date(self) -> datetime.date:
        """
        Get date from Markdown.

        Returns:
            datetime.date: date.

        Raises:
            ValueError: If the date cannot be parsed from the Markdown.
        """
        try:
            date = re.search(
                r'^\d{4}-\d{2}-\d{2}', self.md, re.MULTILINE,
            ).group(0)
        except (re.error, TypeError, IndexError) as error:
            raise ValueError('Failed to fetch date:\n{0}'.format(error))
        return datetime.date.fromisoformat(date)

    @computed_field
    def images(self) -> list[str]:
        """
        Get images from Markdown.

        Returns:
            list[str]: images.

        Raises:
            ValueError: If the images cannot be parsed from the Markdown.
        """
        try:
            images = re.findall(r'!\[.*?\]\((.*?)\)', self.md)
        except re.error as error:
            raise ValueError('Failed to parse images:\n{0}'.format(error))
        if images:
            ta = TypeAdapter(ReachableUrlList)
            try:
                ta.validate_python(images)
            except ValidationError as url_error:
                raise ValueError('Failed to validate images:\n{0}'.format(
                    url_error,
                ))
            return images

    @computed_field
    def description(self) -> str:
        """
        Get description from Markdown.

        Returns:
            str: description.

        Raises:
            ValueError: If the description cannot be parsed from the Markdown.
        """
        try:
            description = re.search(
                r'\d{4}-\d{2}-\d{2}(.*)', self.md, re.DOTALL,
            ).group(1)
        except (re.error, TypeError, IndexError) as description_error:
            raise ValueError('Failed to parse description:\n{0}'.format(
                description_error,
            ))
        try:
            description = re.sub(
                r'!\[.*?\]\(.*?\)', '', description, flags=re.DOTALL,
            )
        except (re.error, TypeError) as cleanup_error:
            raise ValueError('Failed to cleanup description:\n{0}'.format(
                cleanup_error,
            ))
        return description.strip()

    @validate_call
    def hugo(self) -> str:
        """
        Generate Hugo content.

        Returns:
            str: Hugo content string.

        Raises:
            ValueError: If generating the Hugo content fails.
        """
        try:
            front_matter = yaml.safe_dump(self.model_dump(
                exclude_none=True, exclude={'md', 'description'},
            ))
        except yaml.YAMLError as yaml_error:
            raise ValueError('Failed to dump YAML front matter:\n{0}'.format(
                yaml_error,
            ))
        return '---\n{0}---\n{1}'.format(front_matter, self.description)


class Newsfeed(BaseModelForbidExtra):
    """Project newsfeed."""

    project: AnnotatedStr
    md: AnnotatedStr

    @classmethod
    def from_url(cls, url: HttpUrl, project: AnnotatedStr):
        """
        Load newsfeed from a URL.

        Parameters:
            url: Newsfeed URL.
            project: project name.

        Returns:
            Newsfeed object.

        Raises:
            ValueError: if loading the newsfeed fails.
        """
        try:
            with request.urlopen(str(url), timeout=5) as res:  # noqa: S310
                return cls(project=project, md=res.read().decode('utf-8'))
        except (URLError, ValueError, TimeoutError) as urlopen_error:
            raise ValueError("Failed to load newsfeed from '{0}':\n{1}".format(
                url, urlopen_error,
            ))

    @computed_field
    def news(self) -> list[News]:
        """
        Get news from the Markdown.

        Returns:
            list[News]: list of news.

        Raises:
            ValueError: If the news cannot be parsed from the Markdown.
        """
        try:
            matches = re.findall(r'(## .+?)(?=\n## |$)', self.md, re.DOTALL)
        except (re.error, TypeError) as re_error:
            raise ValueError(
                'Failed to process Markdown:\n{0}'.format(re_error),
            )
        news_list = []
        for match in matches:
            try:
                news_list.append(News(newsfeed=[self.project], md=match))
            except (ValidationError, ValueError) as news_error:
                raise ValueError(
                    'Failed to load news:\n{0}'.format(news_error),
                )
        return news_list

    @validate_call
    def dump(self, news_dir: DirectoryPath):
        """
        Dump Hugo content.

        Parameters:
            news_dir: Hugo content directory for news.

        Raises:
            ValueError: if dumping the Hugo content fails.
        """
        for index, news in enumerate(self.news):
            try:
                path = os.path.join(
                    news_dir, '{0}-{1}.md'.format(self.project, index + 1),
                )
            except (TypeError, AttributeError, BytesWarning) as join_error:
                raise ValueError(
                    'Failed to define path:\n{0}'.format(join_error),
                )
            try:
                with open(path, 'w') as news_file:
                    news_file.write(news.hugo())
            except OSError as open_error:
                raise ValueError(
                    "Failed to write file '{0}':\n{1}".format(
                        path, open_error,
                    ),
                )
