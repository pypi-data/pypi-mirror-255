# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Julian Ruestig


import yaml
import argparse
from typing import Any

from os.path import join
from os import makedirs
import subprocess


def get_git_revision_hash() -> str:
    return subprocess.check_output(
        ['git', 'rev-parse', 'HEAD']
    ).decode('ascii').strip()


def convert_float(item: Any) -> Any:
    try:
        return float(item)
    except ValueError:
        return item


def convert_str_to_float(dictionary: dict) -> None:
    for key, value in dictionary.items():
        if isinstance(value, str):
            dictionary[key] = convert_float(value)
        elif isinstance(value, list):
            dictionary[key] = [convert_float(item) if isinstance(item, str)
                               else item for item in value]
        elif isinstance(value, dict):
            convert_str_to_float(value)


def load_and_save_config(default: str) -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config",
        help="Config File",
        type=str,
        nargs='?',
        const=1,
        default=default)
    parser.add_argument(
        '--cpu',
        action='store_true',
        help='Use CPU',
        default=False
    )
    args = parser.parse_args()

    if args.cpu:
        import jax.config
        jax.config.update('jax_platform_name', 'cpu')

    cfg_file = args.config
    with open(cfg_file, 'r') as file:
        cfg = yaml.safe_load(file)

    convert_str_to_float(cfg)
    cfg['git_hash'] = get_git_revision_hash()

    makedirs(cfg['outputdir'], exist_ok=True)
    with open(join(cfg['outputdir'], 'config.yaml'), 'w') as file:
        yaml.dump(cfg, file)

    return cfg
