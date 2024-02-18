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

    if req.status_code != 200:
        logger.error('The token validation request failed.')
        msg = f'The token validation request failed: {req.text}'
        raise HTTPRequestFailed(msg)

    json_response = req.json()
    if 'name' not in json_response:
        logger.error('Malformatted response from validation API.')
        msg = 'Malformatted response from validation API. Please try again.'
        raise HTTPRequestFailed(msg)
