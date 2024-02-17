import json
import platform
import time
import socket
import ssl
import subprocess
import urllib.request
import urllib.error
import urllib.parse

from biolib.biolib_logging import logger_no_user_data
from biolib.typing_utils import Dict, Optional, Union, Literal, cast


def _create_ssl_context():
    context = ssl.create_default_context()
    try:
        if platform.system() == 'Darwin':
            certificates = subprocess.check_output(
                "security find-certificate -a -p",
                shell=True
            ).decode('utf-8')
            context.load_verify_locations(cadata=certificates)
    except BaseException:
        pass
    return context


class HttpError(urllib.error.HTTPError):
    def __init__(self, http_error: urllib.error.HTTPError):
        super().__init__(
            url=http_error.url,
            code=http_error.code,
            msg=http_error.msg,  # type: ignore
            hdrs=http_error.hdrs,  # type: ignore
            fp=http_error.fp
        )

    def __str__(self):
        response_text = self.read().decode('utf-8')
        return f'{self.code} Error: {response_text} for url: {self.url}'


class HttpResponse:
    def __init__(self, response):
        self.status_code = response.status
        self.content = response.read()
        self.url = response.geturl()

    @property
    def text(self) -> str:
        return cast(str, self.content.decode('utf-8'))

    def json(self):
        return json.loads(self.text)


class HttpClient:
    ssl_context = None

    @staticmethod
    def request(
            url: str,
            method: Optional[Literal['GET', 'POST', 'PATCH']] = None,
            data: Optional[Union[Dict, bytes]] = None,
            headers: Optional[Dict[str, str]] = None,
            retries: int = 5,
    ) -> HttpResponse:
        if not HttpClient.ssl_context:
            HttpClient.ssl_context = _create_ssl_context()
        headers_to_send = headers or {}
        if isinstance(data, dict):
            headers_to_send['Accept'] = 'application/json'
            headers_to_send['Content-Type'] = 'application/json'

        request = urllib.request.Request(
            url=url,
            data=json.dumps(data).encode() if isinstance(data, dict) else data,
            headers=headers_to_send,
            method=method or 'GET',
        )
        timeout_in_seconds = 60 if isinstance(data, dict) else 180  # TODO: Calculate timeout based on data size

        last_error: Optional[urllib.error.URLError] = None
        for retry_count in range(retries + 1):
            if retry_count > 0:
                time.sleep(5 * retry_count)
                logger_no_user_data.debug(f'Retrying HTTP {method} request...')
            try:
                with urllib.request.urlopen(
                    request,
                    context=HttpClient.ssl_context,
                    timeout=timeout_in_seconds
                ) as response:
                    return HttpResponse(response)

            except urllib.error.HTTPError as error:
                if error.code == 502:
                    logger_no_user_data.debug(f'HTTP {method} request failed with status 502 for "{url}"')
                    last_error = error
                elif error.code == 503:
                    logger_no_user_data.debug(f'HTTP {method} request failed with status 503 for "{url}"')
                    last_error = error
                else:
                    raise HttpError(error) from None

            except urllib.error.URLError as error:
                if isinstance(error.reason, socket.timeout):
                    logger_no_user_data.debug(f'HTTP {method} request failed with read timeout for "{url}"')
                    last_error = error
                else:
                    raise error

        raise last_error or Exception(f'HTTP {method} request failed after {retries} retries for "{url}"')
