import re
from uploader.zipper import find_files


def test_find_files():
    reg = re.compile(r'.*\.xml')
    result = find_files(reg, 'tests/fixtures/test_results/')
    elements = [
        'tests/fixtures/test_results/pydriller_testresults.xml',
        'tests/fixtures/test_results/examples/pydriller_testresults.xml',
        'tests/fixtures/test_results/examples1/pydriller_testresults1.xml',
        'tests/fixtures/test_results/examples1/examples2/' +
        'pydriller_testresults2.xml',
        'tests/fixtures/test_results/.testpulse.yaml',
    ]
    for el in elements:
        assert el in result
    assert len(elements) == len(result)


def test_find_files_exclude_dir():
    reg = re.compile(r'.*\.xml')
    result = find_files(reg, 'tests/fixtures/test_results_exclude_dirs/')
    elements = [
        'tests/fixtures/test_results_exclude_dirs/pydriller_testresults.xml',
    ]
    for el in elements:
        assert el in result
    assert len(elements) == len(result)
