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
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        raise Exception('Path "{}" does not exist'.format(path))

    if not username:
        username = os.environ.get('GIT_USERNAME', '')
        if not username:
            raise Exception('Invalid username value: {}'.format(username))

    os.environ['GIT_ASKPASS'] = os.path.join(project_dir, 'askpass.py')
    os.environ['GIT_USERNAME'] = username
    os.environ['GIT_PASSWORD'] = password or os.environ.get('GIT_PASSWORD', None) or getpass()

    for p in sorted((i for i in os.listdir(path) if not i.startswith('.') and i not in skip)):
        directory = os.path.join(path, p)
        logger.debug('Checking out path {}'.format(directory))

        if os.path.isdir(directory):
            g = git.cmd.Git(directory)
            try:
                g.checkout(branch)

            except git.exc.GitCommandError:
                logger.error(traceback.format_exc())

            else:
                g.pull()


if __name__ == "__main__":
    run()
