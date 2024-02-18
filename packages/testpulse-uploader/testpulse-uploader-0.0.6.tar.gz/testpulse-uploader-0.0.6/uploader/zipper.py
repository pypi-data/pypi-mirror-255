import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Pattern, List
from zipfile import ZipFile

logger = logging.getLogger(__name__)

excluded_dirs = (
    ".git",
    ".venv",
    "venv",
)

TESTPULSE_CONFIG_FILE = '.testpulse.yaml'


def exclude_directory(directory: str) -> bool:
    for excluded_dir in excluded_dirs:
        if excluded_dir in directory:
            return True
    return False


def find_files(regex_pattern: Pattern[str], root: Path) -> List[str]:
    test_results = []
    for dirpath, _, filenames in os.walk(root):
        if exclude_directory(directory=dirpath):
            continue

        for file in filenames:
            filename = os.path.join(dirpath, file)
            if regex_pattern.search(filename):
                test_results.append(filename)

    if not test_results:
        logger.info("We did not find any file using the REGEX passed via parameters. Please check the files are there.")
        return test_results

    config_file = find_config_file(root=root)
    if config_file:
        test_results.append(config_file)

    return test_results


def find_config_file(root: Path) -> Optional[str]:
    path_to_config_file = os.path.join(root, TESTPULSE_CONFIG_FILE)
    if os.path.exists(path_to_config_file):
        return path_to_config_file
    return None


def zip_files(files_list: List[str], root: Path) -> Optional[str]:
    if not files_list:
        logger.info('Preemptive return since list of files is empty.')
        return None

    zip_file = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    with ZipFile(zip_file.name, 'w') as zip:
        for file in files_list:
            filep = Path(file)
            zip.write(filep, filep.relative_to(root))
    return zip_file.name
