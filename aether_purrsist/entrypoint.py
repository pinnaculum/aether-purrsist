import argparse
import os
from pathlib import Path

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


from tortoise import Tortoise, run_async

from . import purrsist


async def init():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',
                        '-c',
                        default='config.yaml',
                        dest='config',
                        help='Configuration file path')
    args = parser.parse_args()

    with open(args.config, 'rt') as fd:
        cfg = yaml.load(fd, Loader=Loader)

    home = Path(os.getenv('HOME'))
    aethcfgp = home.joinpath('.config').joinpath(
        'Air Labs').joinpath('Aether')

    dbpath = Path(cfg.get('db_path',
                          str(aethcfgp.joinpath('backend').joinpath(
                              'AetherDB.db'))
                          ))

    if not dbpath.is_file():
        raise ValueError(f'DB file {dbpath} does not exist')

    await Tortoise.init(
        db_url=f'sqlite://{dbpath}',
        modules={'models': ['aether_purrsist.models']}
    )
    await Tortoise.generate_schemas()

    await purrsist.purrsist(cfg)


def start():
    run_async(init())
