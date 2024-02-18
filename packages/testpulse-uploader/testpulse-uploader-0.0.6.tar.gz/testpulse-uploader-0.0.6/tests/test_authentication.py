import os
import responses
import pytest

from unittest import mock
from uploader.authentication import authenticate
from uploader.exceptions import HTTPRequestFailed

env_variables_mocked = {
    "GITHUB_REPOSITORY_OWNER": "testpulse-io",
    "TESTPULSE_TOKEN": "MYVERYLONGANDIMPOSSIBLETOGUESSTOKEN",
}


@responses.activate
@mock.patch.dict(os.environ, env_variables_mocked)
def test_authenticate_404():
    # Register via 'Response' object
    rsp1 = responses.Response(
        method="GET",
        url="https://testpulse-io-api.fly.dev/api/tokens/check",
        status=404
    )
    responses.add(rsp1)

    with pytest.raises(HTTPRequestFailed, match='The token validation request failed.*'):
        authenticate()


@responses.activate
@mock.patch.dict(os.environ, env_variables_mocked)
def test_authenticate_malformatted():
    # Register via 'Response' object
    rsp1 = responses.Response(
        method="GET",
        url="https://testpulse-io-api.fly.dev/api/tokens/check",
        status=200,
        json={"noname": "there is no name in the reply"}
    )
    responses.add(rsp1)

    with pytest.raises(HTTPRequestFailed, match='Malformatted response from validation API.*'):
        authenticate()


@responses.activate
@mock.patch.dict(os.environ, env_variables_mocked)
def test_authenticate_valid():
    # Register via 'Response' object
    rsp1 = responses.Response(
        method="GET",
        url="https://testpulse-io-api.fly.dev/api/tokens/check",
        status=200,
        json={'id': 1234, 'name': 'testpulse-io'}
    )
    responses.add(rsp1)

    authenticate()
