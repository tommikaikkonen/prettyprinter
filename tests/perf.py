from prettyprinter import pformat
import json


def main():
    with open('tests/sample_json.json') as f:
        data = json.load(f)

    pformat(data)


if __name__ == '__main__':
    main()
