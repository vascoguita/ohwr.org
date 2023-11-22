# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Load, parse and validate news."""

import re
from datetime import date
from typing import Optional
from urllib import request
from dataclasses import dataclass

from markdown import Markdown, Section
from pydantic import BaseModel, Field
from url import URL


class NewsError(Exception):
    """Failed to load, parse, validate or dump news."""


class News(BaseModel, extra='forbid'):
    title: str
    date: date
    topics: Optional[list[str]] = Field(default_factory=list)
    images: Optional[list[URL]] = None
    description: Optional[str] = None

    @classmethod
    def from_markdown(cls, section: Section):
        before, _, after = map(str.strip, section.markdown.partition('\n'))
        parsed_date = date.fromisoformat(before)
        topics = []
        if after.startswith('Topics:'):
            before, _, after = after.partition('\n')
            before = before.lstrip('Topics:')
            topics = list(map(str.strip, before.split(',')))
        return cls(
            title=section.heading,
            date=parsed_date,
            topics=topics,
            images=re.findall(r'\!\[.*?\]\((.*?)\)', after),
            description=re.sub(r'\!\[.*?\]\(.*?\)', '', after),
        )

@dataclass
class Newsfeed(object):
    news: list[News]

    @classmethod
    def from_url(cls, url: str):
        with request.urlopen(url) as response:  # noqa: S310
            return cls.from_markdown(Markdown(response.read().decode()))

    @classmethod
    def from_markdown(cls, markdown: Markdown):
        newsfeed_section = markdown.find('News')
        if not newsfeed_section:
            raise NewsError('No News section found in Markdown')
        news = []
        for news_section in newsfeed_section.sections:
            news.append(News.from_markdown(news_section))
        return cls(news)
