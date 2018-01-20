import sys

from prettyprinter import set_default_config

# Need this to deterministically test on Python 3.5
set_default_config(sort_dict_keys=True)


def pytest_ignore_collect(path, config):
    if 'test_dataclasses' in str(path) and sys.version_info < (3, 7):
        return True
