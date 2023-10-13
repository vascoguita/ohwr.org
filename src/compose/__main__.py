# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""CLI to generate content for ohwr.org."""

import argparse
import json
import logging
from urllib.request import urlopen

from config import Config, ConfigError
import yaml
from sources import ProjSources

parser = argparse.ArgumentParser()
parser.add_argument('config', type=argparse.FileType('r'))
args = parser.parse_args()
config = yaml.safe_load(args.config)

logging.basicConfig(
    level=getattr(logging, config['log_level']),
    format='%(asctime)s - %(levelname)s - %(message)s',  # noqa: WPS323
)

with open(config['licenses']) as json_licenses:
    spdx_license_list = json.load(json_licenses)

for proj in config['projects']:
    try:
        proj_config = Config.from_repo(proj['repo'])
    except ConfigError as error:
        msg = 'Could not configure project from {0}:\n↳ {1}'
        logging.error(msg.format(proj['repo'], error))
        continue
    proj_sources = ProjSources.from_config(proj_config)
    proj_sources.dump(local_config['source'])
