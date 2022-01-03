#! /usr/bin/env python3

import os
import sys
from pathlib import Path

import click
import git
import logging
import traceback
from getpass import getpass
from pyconfigreader import ConfigReader
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


def exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


# Install exception handler
sys.excepthook = exception_handler

# Load configuration
project_dir = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
with ConfigReader(os.path.join(project_dir, 'settings.ini')) as config:
    DEFAULT_USERNAME = config.get('username')
    WORKERS = config.get('workers', default='7')


@click.command()
@click.option('--username', '-u', default=DEFAULT_USERNAME, help='Repo username')
@click.option('--branch', '-b', default='master', help='Branch name')
@click.option('--password', '-p', default=None, help='Password')
@click.option('--skip', '-k', default=[], multiple=True, help='Directory names to skip. Can be used multiple times.')
@click.argument('path')
def run(username, branch, password, skip, path):
    """Git pull repositories in a certain directory.

    Useful if you have a couple of git repositories in a certain directory and you would like to bulk pull
    """
    path = Path(path)
    if not path.is_dir():
        click.echo('Path "{}" does not exist'.format(path))
        sys.exit(1)

    if not username:
        username = os.environ.get('GIT_USERNAME', '')
        if not username:
            click.echo('Invalid username value: {}'.format(username))
            sys.exit(1)

    os.environ['GIT_ASKPASS'] = os.path.join(project_dir, 'askpass.py')
    os.environ['GIT_USERNAME'] = username
    os.environ['GIT_PASSWORD'] = password or os.environ.get('GIT_PASSWORD', None) or getpass()

    def do_checkout(dir_):
        logger.debug('Checking out path {}'.format(dir_))
        g = git.cmd.Git(dir_)
        try:
            g.checkout(branch)

        except Exception:
            logger.error('Error at {}'.format(dir_), exc_info=True)
            # logger.error(traceback.format_exc())

        else:
            g.pull()

    valid_dirs = []
    skips = set()

    ignore_file = path / '.refreshignore'
    if ignore_file.is_file():
        with ignore_file.open() as f:
            skips = {l.strip() for l in f.readlines()}

    skips = skips | set(skip)

    iterator = (p for p in path.iterdir() if p.is_dir() and p.name[0] != '.' and p.name not in skips)
    for p in sorted(iterator, key=lambda x: x.name):
        directory = str(p.absolute())
        logger.debug('Adding path {}'.format(directory))

        valid_dirs.append(directory)

    executor = ThreadPoolExecutor(max_workers=WORKERS)
    executor.map(do_checkout, valid_dirs)


if __name__ == "__main__":
    run()
