import logging
import click
from biolib.biolib_download_container import download_container_from_uri
from biolib.biolib_logging import logger, logger_no_user_data


@click.command(help='Push an application to BioLib', name='download-container')
@click.argument('uri')
def download_container(uri: str) -> None:
    logger.configure(default_log_level=logging.INFO)
    logger_no_user_data.configure(default_log_level=logging.INFO)
    download_container_from_uri(uri)
