import os
import responses
import pytest

from pathlib import Path
from unittest import mock
from uploader.exceptions import NotInCI
from uploader.upload import generate_data_and_headers, upload_test_results
from uploader.urls import ENDPOINT_UPLOAD_RESULTS, TESTPULSE_RECEIVER

env_variables_mocked = {
    "GITHUB_REPOSITORY": "testpulse/myrepo",
    "GITHUB_SHA": "0289dbc9db2214d7b3e2a115987c3067b4400f25",
    "GITHUB_REF": "refs/remotes/origin/main",
    "TESTPULSE_TOKEN": "MYVERYLONGANDIMPOSSIBLETOGUESSTOKEN",
    "GITHUB_ACTIONS": "True",
}

url = TESTPULSE_RECEIVER + ENDPOINT_UPLOAD_RESULTS


@responses.activate
@mock.patch.dict(os.environ, env_variables_mocked)
def test_simple_false():
    # Register via 'Response' object
    rsp1 = responses.Response(
        method="POST",
        url=url,
        status=404
    )
    responses.add(rsp1)

    resp2 = upload_test_results(zip=Path('tests/fixtures/test_results.zip'),
                                localhost=False)

    assert resp2 is False


@responses.activate
@mock.patch.dict(os.environ, env_variables_mocked)
def test_simple_true():
    # Register via 'Response' object
    rsp1 = responses.Response(
        method="POST",
        url=url,
        status=200
    )
    responses.add(rsp1)

    resp2 = upload_test_results(zip=Path('tests/fixtures/test_results.zip'),
                                localhost=False)

    assert resp2 is True


@mock.patch.dict(os.environ, env_variables_mocked)
def test_generate_data_and_headers_mocked():
    data, token = generate_data_and_headers()

    assert data['commit'] == "0289dbc9db2214d7b3e2a115987c3067b4400f25"
    assert data['repository'] == "testpulse/myrepo"
    assert token == "MYVERYLONGANDIMPOSSIBLETOGUESSTOKEN"


def test_generate_data_and_headers_not_existing():
    with pytest.raises(NotInCI):
        generate_data_and_headers()
