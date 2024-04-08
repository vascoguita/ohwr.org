# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Custom Pydantic utilities."""


from http import HTTPMethod, HTTPStatus
from typing import Annotated
from urllib import request
from urllib.error import URLError

from pydantic import (
    AfterValidator,
    BaseModel,
    Field,
    HttpUrl,
    StringConstraints,
)


class BaseModelForbidExtra(BaseModel, extra='forbid'):
    """Custom base class for Pydantic models with extra='forbid'."""


AnnotatedStr = Annotated[str, StringConstraints(
    strip_whitespace=True,
    min_length=1,
)]
AnnotatedStrList = Annotated[list[AnnotatedStr], Field(min_length=1)]


def is_reachable(url: HttpUrl) -> HttpUrl:
    """
    Check if the URL is reachable.

    Parameters:
        url: HTTP URL.

    Returns:
        HTTP URL.

    Raises:
        ValueError: if the URL is not reachable.
    """
    req = request.Request(url, method=HTTPMethod.HEAD)
    try:
        with request.urlopen(req, timeout=5) as res:  # noqa: S310
            if res.status != HTTPStatus.OK:
                raise ValueError("Status code: '{0}'.".format(res.status))
    except (URLError, ValueError) as error:
        error_fmt = "Failed to access URL: '{0}'."
        raise ValueError(error_fmt.format(url)) from error
    return url


Url = Annotated[HttpUrl, AfterValidator(is_reachable)]
UrlList = Annotated[list[Url], Field(min_length=1)]
