#! /usr/bin/env python3

import os
import sys
import click
import git
import logging
import traceback
from getpass import getpass
from pyconfigreader import ConfigReader

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


def refresh_dirs_in_path(path):
    logger.debug('Checking out path {}'.format(path))
    for p in sorted(os.listdir(path)):
        directory = os.path.join(path, p)

        if os.path.isdir(directory):
            g = git.cmd.Git(directory)
            try:
                g.pull()
            except git.exc.GitCommandError:
                logger.error(traceback.format_exc())


@click.command()
@click.option('--username', default=DEFAULT_USERNAME, help='Repo username')
@click.argument('path')
def run(username, path):
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        raise Exception('{} does not exist'.format(path))

    if not username:
        raise Exception('Invalid username value: {}'.format(username))

    os.environ['GIT_ASKPASS'] = os.path.join(project_dir, 'askpass.py')
    os.environ['GIT_USERNAME'] = username
    os.environ['GIT_PASSWORD'] = getpass()

    refresh_dirs_in_path(path)


if __name__ == "__main__":
    run()
