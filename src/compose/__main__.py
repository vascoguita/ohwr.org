# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

"""CLI to generate content for ohwr.org."""

import argparse
import logging

import yaml
from config import Config
from license import LicenseValidator

parser = argparse.ArgumentParser()
parser.add_argument('config', type=argparse.FileType('r'))
args = parser.parse_args()

config = Config(**yaml.safe_load(args.config))

logging.basicConfig(
    level=getattr(logging, config['log_level']),
    format='%(asctime)s - %(levelname)s - %(message)s',  # noqa: WPS323
)

LicenseValidator.config(config.licenses)

