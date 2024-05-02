# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""Generate content for ohwr.org."""

import argparse
import logging
import os
import sys

from config import Config
from license import SpdxLicenseList
from news import Newsfeed
from pydantic import ValidationError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',  # noqa: WPS323
)

parser = argparse.ArgumentParser()
parser.add_argument('config', type=argparse.FileType('r'))
args = parser.parse_args()

logging.info("Loading configuration from '{0}'...".format(args.config.name))
try:
    config = Config.from_yaml(args.config.read())
except (ValidationError, ValueError) as config_error:
    logging.error('Failed to load configuration:\n{0}'.format(config_error))
    sys.exit(1)

logging.info("Loading SPDX license list from '{0}'...".format(config.licenses))
try:
    SpdxLicenseList.from_file(config.licenses)
except (ValidationError, ValueError) as spdx_error:
    logging.error('Failed to load SPDX license list:\n{0}'.format(spdx_error))
    sys.exit(1)

for category in config.categories:
    logging.info('{0} - Generating category page...'.format(category.name))
    try:
        category.dump(config.sources)
    except (ValidationError, ValueError) as category_error:
        logging.error('{0} - Failed to generate category page:\n{1}'.format(
            category.name, category_error,
        ))
        sys.exit(1)

proj_dir = os.path.join(config.sources, 'content/projects')
try:
    os.makedirs(proj_dir)
except OSError as projects_dir_error:
    logging.error("Failed to create '{0}' directory:\n{1}".format(
        proj_dir, projects_dir_error,
    ))
    sys.exit(1)

news_dir = os.path.join(config.sources, 'content/news')
try:
    os.makedirs(news_dir)
except OSError as news_dir_error:
    logging.error("Failed to create '{0}' directory:\n{1}".format(
        news_dir, news_dir_error,
    ))
    sys.exit(1)

for project in config.projects:
    logging.info('{0} - Generating project page...'.format(project.id))
    try:
        project.dump(proj_dir)
    except (ValidationError, ValueError) as project_error:
        logging.error('{0} - Failed to generate project page:\n{1}'.format(
            project.id, project_error,
        ))
        continue

    if project.manifest.newsfeed:
        logging.info("{0} - Loading newsfeed'...".format(project.id))
        try:
            newsfeed = Newsfeed.from_url(project.manifest.newsfeed, project.id)
        except ValueError as newsfeed_error:
            logging.error("{0} - Failed to load newsfeed:\n{2}".format(
                project.id, newsfeed_error,
            ))
            continue

        for index, news in enumerate(newsfeed):
            name = '{0}-{1}'.format(project.id, index + 1)
            logging.info('{0} - Generating news page...'.format(name))
            try:
                news.dump(os.path.join(news_dir, '{0}.md'.format(name)))
            except (ValidationError, ValueError) as news_error:
                logging.error(
                    '{0} - Failed to generate news page:\n{1}'.format(
                        name, news_error,
                    ),
                )
