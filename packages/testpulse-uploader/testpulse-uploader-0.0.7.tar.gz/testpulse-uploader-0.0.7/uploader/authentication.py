import logging
import requests
from uploader.exceptions import HTTPRequestFailed
from uploader.urls import ENDPOINT_TOKENS_CHECK, TESTPULSE_API
from uploader.domain import TokenVerification

logger = logging.getLogger(__name__)


def authenticate() -> None:
    token_verifier = TokenVerification()

    payload = {
        'token': token_verifier.token
    }

    url = TESTPULSE_API + ENDPOINT_TOKENS_CHECK
    req = requests.get(url=url,
                       params=payload)

    print(req)
    if req.status_code != 200:
        logger.error('The token validation request failed.')
        msg = f'The token validation request failed: {req.text}'
        raise HTTPRequestFailed(msg)

    # Maybe in the future we need to save the response somewhere.
    # json_response = req.json()
