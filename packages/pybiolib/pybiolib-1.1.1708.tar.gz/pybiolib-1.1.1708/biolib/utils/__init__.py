import collections.abc
import multiprocessing
import os
import time
import socket
import sys

from typing import Optional
import requests
from importlib_metadata import version, PackageNotFoundError

from biolib.utils.seq_util import SeqUtil, SeqUtilRecord

# try fetching version, if it fails (usually when in dev), add default
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger_no_user_data, logger
from biolib.typing_utils import Tuple, Iterator
from .multipart_uploader import MultiPartUploader, get_chunk_iterator_from_bytes

try:
    BIOLIB_PACKAGE_VERSION = version('pybiolib')
except PackageNotFoundError:
    BIOLIB_PACKAGE_VERSION = '0.0.0'

IS_DEV = os.getenv('BIOLIB_DEV', '').upper() == 'TRUE'


def load_base_url_from_env() -> str:
    base_url = os.getenv('BIOLIB_BASE_URL')
    if base_url:
        return base_url.lower().rstrip('/')

    try:
        search_list = []
        with open('/etc/resolv.conf') as file:
            for line in file:
                line_trimmed = line.strip()
                if line_trimmed.startswith('search'):
                    search_list = line_trimmed.split()[1:]
                    logger.debug(f'Found search list: {search_list} when resolving base url.')
                    break

        for search_host in search_list:
            host_to_try = f'biolib.{search_host}'
            try:
                if len(socket.getaddrinfo(host_to_try, 443)) > 0:
                    return f'https://{host_to_try}'.lower()
            except BaseException:  # pylint: disable=broad-except
                pass
    except BaseException:  # pylint: disable=broad-except
        pass

    return 'https://biolib.com'


BIOLIB_BASE_URL: Optional[str] = None
BIOLIB_SITE_HOSTNAME: Optional[str] = None

BIOLIB_CLOUD_BASE_URL = os.getenv('BIOLIB_CLOUD_BASE_URL', '').lower()

BIOLIB_PACKAGE_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BIOLIB_CLOUD_ENVIRONMENT = os.getenv('BIOLIB_CLOUD_ENVIRONMENT', '').lower()

BIOLIB_SECRETS_TMPFS_PATH = os.environ.get('BIOLIB_SECRETS_TMPFS_PATH')

IS_RUNNING_IN_CLOUD = BIOLIB_CLOUD_ENVIRONMENT == 'non-enclave'

BASE_URL_IS_PUBLIC_BIOLIB: Optional[bool] = None

# sys.stdout is an instance of OutStream in Jupyter and Colab which does not have .buffer
if not hasattr(sys.stdout, 'buffer'):
    IS_RUNNING_IN_NOTEBOOK = True
else:
    IS_RUNNING_IN_NOTEBOOK = False

STREAM_STDOUT = False

if BIOLIB_CLOUD_ENVIRONMENT and not IS_RUNNING_IN_CLOUD:
    logger_no_user_data.warning((
        'BIOLIB_CLOUD_ENVIRONMENT defined but does not specify the cloud environment correctly. ',
        'The compute node will not act as a cloud compute node'
    ))

ByteRangeTuple = Tuple[int, int]
DownloadChunkInputTuple = Tuple[ByteRangeTuple, str]


def _download_chunk(input_tuple: DownloadChunkInputTuple) -> bytes:
    max_download_retries = 10

    byte_range, presigned_url = input_tuple
    start, end = byte_range

    for retry_attempt in range(max_download_retries):
        if retry_attempt > 0:
            logger_no_user_data.debug(f'Attempt number {retry_attempt} for part {start}')
        try:
            response = requests.get(
                url=presigned_url,
                stream=True,
                headers={'range': f'bytes={start}-{end}'},
                timeout=300,  # timeout after 5 min
            )
            if response.ok:
                return_value: bytes = response.raw.data
                logger_no_user_data.debug(f'Returning raw data for part {start}')
                return return_value
            else:
                logger_no_user_data.warning(
                    f'Got not ok response when downloading part {start}:{end}. '
                    f'Got response status {response.status_code} and content: {response.content.decode()} '
                    f'Retrying...'
                )
        except Exception:  # pylint: disable=broad-except
            logger_no_user_data.warning(f'Encountered error when downloading part {start}:{end}. Retrying...')

        time.sleep(5)

    logger_no_user_data.debug(f'Max retries hit, when downloading part {start}:{end}. Exiting...')
    raise BioLibError(f'Max retries hit, when downloading part {start}:{end}. Exiting...')


class ChunkIterator(collections.abc.Iterator):

    def __init__(self, file_size: int, chunk_size: int, presigned_url: str):
        self._semaphore = multiprocessing.BoundedSemaphore(20)  # support 20 chunks to be processed at once
        self._iterator = self._get_chunk_input_iterator(file_size, chunk_size, presigned_url)

    def __iter__(self):
        return self

    def __next__(self):
        if self._semaphore.acquire(timeout=1800):
            return next(self._iterator)
        else:
            raise Exception('Did not receive work within 30 min.')

    def chunk_completed(self) -> None:
        self._semaphore.release()

    @staticmethod
    def _get_chunk_input_iterator(
            file_size: int,
            chunk_size: int,
            presigned_url: str,
    ) -> Iterator[DownloadChunkInputTuple]:
        for index in range(0, file_size, chunk_size):
            byte_range: ByteRangeTuple = (index, index + chunk_size - 1)
            yield byte_range, presigned_url


def download_presigned_s3_url(presigned_url: str, output_file_path: str) -> None:
    chunk_size = 50_000_000

    with requests.get(presigned_url, stream=True, headers={'range': 'bytes=0-1'}) as response:
        if not response.ok:
            raise Exception(f'Got response status code {response.status_code} and content {response.content.decode()}')

        file_size = int(response.headers['Content-Range'].split('/')[1])

    chunk_iterator = ChunkIterator(file_size, chunk_size, presigned_url)

    bytes_written = 0
    # use 16 cores, unless less is available
    process_pool = multiprocessing.Pool(processes=min(16, multiprocessing.cpu_count() - 1))
    try:
        with open(output_file_path, 'ab') as output_file:
            for index, data in enumerate(process_pool.imap(_download_chunk, chunk_iterator)):
                logger_no_user_data.debug(f'Writing part {index} to file...')
                output_file.write(data)

                bytes_written += chunk_size
                approx_progress_percent = min(bytes_written / file_size * 100, 100)
                logger_no_user_data.debug(
                    f'Wrote part {index} of {file_size} to file, '
                    f'the approximate progress is {round(approx_progress_percent, 2)}%'
                )
                chunk_iterator.chunk_completed()
    finally:
        logger_no_user_data.debug('Closing process poll...')
        process_pool.close()
        logger_no_user_data.debug('Process poll closed.')
