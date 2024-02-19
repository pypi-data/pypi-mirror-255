#!/usr/bin/env python3

import argparse
import logging
from pathlib import Path
import re
from typing import Optional, Pattern
from uploader.authentication import authenticate

from uploader.upload import upload_test_results
from uploader.zipper import find_files, zip_files

logging.basicConfig(format='%(asctime)s-%(levelname)s:%(filename)s:%(lineno)d %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def regex_pattern(regex: str) -> Optional[Pattern[str]]:
    if not regex:
        return None

    try:
        return re.compile(regex)
    except re.error:
        msg = f"String '{regex}' is not valid regex pattern"
        raise argparse.ArgumentTypeError(msg)


def create_parser() -> argparse.ArgumentParser:
    """Parse known test runner arguments.

    Returns:
        argparse.Namespace: namespace of parsed argument values
    """
    parser = argparse.ArgumentParser(
                    prog='upload.py',
                    description='Upload test results for futher processing',
                    epilog='testpulse-io')

    parser.add_argument(
        "-c",
        "--commit",
        type=str,
        default="master",
        help="Commit where the tests run on",
    )

    parser.add_argument(
        "-tr",
        "--test-results-regex",
        required=True,
        help="Regex pattern to find test results XML files",
        type=regex_pattern,
    )

    parser.add_argument(
        "-p",
        "--port",
        default=8080,
        type=int,
        help="Port used to communicate with testpulse-receiver",
    )

    parser.add_argument(
        "-l",
        "--localhost",
        help="Regex pattern to find test results XML files",
        action='store_true'
    )

    return parser


def run(args: argparse.Namespace) -> None:
    root = Path().resolve()
    logger.info('Authenticating...')
    authenticate()
    logger.info('Authenticated successfully.')

    logger.info('Finding files and zipping...')
    selected_files = find_files(args.test_results_regex, root=root)
    zip_file_name = zip_files(files_list=selected_files, root=root)
    if zip_file_name is None:
        return

    logger.info(f'Saved zip file in {zip_file_name}.')

    logger.info('Uploading to our backend server...')
    req = upload_test_results(Path(zip_file_name), localhost=args.localhost)

    if req is True:
        logger.info('Upload was successful!')


def main():
    parser = create_parser()
    args = parser.parse_args()
    run(args=args)


if __name__ == '__main__':
    main()
