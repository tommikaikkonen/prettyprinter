import sys


def pytest_ignore_collect(path, config):
    if 'test_dataclasses' in str(path) and sys.version_info < (3, 7):
        return True
