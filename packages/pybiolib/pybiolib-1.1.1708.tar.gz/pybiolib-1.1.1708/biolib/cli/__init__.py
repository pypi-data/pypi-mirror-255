import logging
import sys

import click

from biolib import utils
from biolib.biolib_logging import logger, logger_no_user_data
from biolib.cli import init, lfs, push, run, start, runtime, download_container


@click.version_option(version=utils.BIOLIB_PACKAGE_VERSION, prog_name='pybiolib')
@click.group(context_settings=dict(help_option_names=['-h', '--help']))
def cli() -> None:
    logger_no_user_data.debug(f'pybiolib {utils.BIOLIB_PACKAGE_VERSION}')
    logger_no_user_data.debug(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')
    utils.STREAM_STDOUT = True

    # set more restrictive default log level for CLI
    logger.configure(default_log_level=logging.WARNING)
    logger_no_user_data.configure(default_log_level=logging.WARNING)


cli.add_command(init.init)
cli.add_command(lfs.lfs)
cli.add_command(push.push)
cli.add_command(run.run)
cli.add_command(runtime.runtime)
cli.add_command(start.start)
cli.add_command(download_container.download_container)

# allow this script to be called without poetry in dev e.g. by an IDE debugger
if utils.IS_DEV and __name__ == '__main__':
    cli()
