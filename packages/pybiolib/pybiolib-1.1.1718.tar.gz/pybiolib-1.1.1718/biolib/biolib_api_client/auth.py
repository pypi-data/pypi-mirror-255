from requests.auth import AuthBase  # type: ignore

from biolib import api
from biolib.biolib_api_client.api_client import UserTokens
from biolib.typing_utils import TypedDict, Literal


class BearerAuth(AuthBase):
    def __init__(self, access_token=None):
        self.access_token = access_token

    def __call__(self, req):
        if self.access_token:
            req.headers['Authorization'] = 'Bearer ' + self.access_token
        return req


class AuthChallengeCreate(TypedDict):
    token: str


class _AuthChallengeStatus(TypedDict):
    state: Literal['awaiting', 'completed']


class AuthChallengeStatus(_AuthChallengeStatus, total=False):
    user_tokens: UserTokens


class BiolibAuthChallengeApi:

    @staticmethod
    def create_auth_challenge() -> AuthChallengeCreate:
        response = api.client.post(path='/user/auth_challenges/')
        response_dict: AuthChallengeCreate = response.json()
        return response_dict

    @staticmethod
    def get_auth_challenge_status(token: str) -> AuthChallengeStatus:
        response = api.client.get(
            path='/user/auth_challenges/',
            headers={'Auth-Challenge-Token': token},
        )

        response_dict: AuthChallengeStatus = response.json()
        return response_dict
