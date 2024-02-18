import logging
from typing import Dict, Optional, Tuple
import requests

from pathlib import Path
from uploader.urls import ENDPOINT_UPLOAD_RESULTS, TESTPULSE_RECEIVER

from uploader.domain import TestRun

logger = logging.getLogger(__name__)

LOCAL_URL = 'http://localhost:8080'


def upload_test_results(zip: Path, localhost: bool) -> Optional[bool]:
    files = {'file': open(zip, 'rb')}

    data, token = generate_data_and_headers()

    headers = {
        "Authorization": f"Bearer {token}",
    }

    url = LOCAL_URL if localhost else TESTPULSE_RECEIVER
    url = url + ENDPOINT_UPLOAD_RESULTS

    logging.debug(f'Making request to {url}')

    req = requests.post(url=url,
                        files=files,
                        data=data,
                        headers=headers)
    if req.status_code != 200:
        logging.error(f'Something went wrong: {req.text}')
        return False
    return True


def generate_data_and_headers() -> Tuple[Dict[str, str], str]:
    upload_data = TestRun()

    data = {
        "commit": upload_data.commit,
        "repository": upload_data.repository,
    }

    return data, upload_data.token
