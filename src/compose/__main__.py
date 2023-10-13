# SPDX-FileCopyrightText: 2023 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""CLI to generate content for ohwr.org."""

import argparse
import json
import logging
from pathlib import Path
from urllib.request import Request, urlopen

import yaml
from config import Config, ConfigError
from sources import ProjSources

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--log-level', default='INFO')
parser.add_argument('-c', '--config', type=Path, default=Path('config.yaml'))
parser.add_argument('-s', '--source', type=Path, default=Path.cwd())
args = parser.parse_args()

logging.basicConfig(
    level=getattr(logging, args.log_level),
    format='%(asctime)s - %(levelname)s - %(message)s',  # noqa: WPS323
)

with open(args.config) as yaml_config:
    config = yaml.safe_load(yaml_config)

req = Request(
    'https://api.github.com/repos/spdx/license-list-data/contents/{0}'.format(
        'json/licenses.json',
    ),
    headers={'Accept': 'application/vnd.github.v3.raw'},
)
with urlopen(req) as response:  # noqa: S310
    spdx_license_list = json.load(response)

for proj in config['projects']:
    try:
        proj_config = Config.from_repo(proj['repo'])
    except ConfigError as error:
        msg = 'Could not configure project from {0}:\n↳ {1}'
        logging.error(msg.format(proj['repo'], error))
        continue
    proj_sources = ProjSources.from_config(proj_config)
    proj_sources.dump(local_config['source'])
