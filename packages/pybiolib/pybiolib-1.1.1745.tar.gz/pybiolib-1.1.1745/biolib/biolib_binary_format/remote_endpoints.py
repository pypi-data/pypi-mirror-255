from datetime import datetime, timedelta
# from urllib.parse import urlparse, parse_qs

from biolib.biolib_logging import logger

from biolib.biolib_api_client.biolib_job_api import BiolibJobApi
from biolib.biolib_binary_format.utils import RemoteEndpoint


class RemoteJobStorageResultEndpoint(RemoteEndpoint):
    def __init__(self, job_id: str, job_auth_token: str):
        self._job_id = job_id
        self._job_auth_token = job_auth_token
        self._expires_at = None
        self._presigned_url = None

    def get_remote_url(self):
        if not self._presigned_url or datetime.utcnow() > self._expires_at:
            self._presigned_url = BiolibJobApi.get_job_storage_download_url(
                job_auth_token=self._job_auth_token,
                job_uuid=self._job_id,
                storage_type='results'
            )
            self._expires_at = datetime.utcnow() + timedelta(minutes=8)
            # TODO: Use expires at from url
            # parsed_url = urlparse(self._presigned_url)
            # query_params = parse_qs(parsed_url.query)
            # time_at_generation = datetime.datetime.strptime(query_params['X-Amz-Date'][0], '%Y%m%dT%H%M%SZ')
            # self._expires_at = time_at_generation + timedelta(seconds=int(query_params['X-Amz-Expires'][0]))
            logger.debug(f'Job "{self._job_id}" fetched presigned URL with expiry at {self._expires_at.isoformat()}')

        return self._presigned_url
