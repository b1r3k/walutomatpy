import os.path
import json


def read_fixture(filename, mode='r', decoder=json.loads):
    filepath = os.path.join('tests/fixtures', filename)
    with open(filepath, mode) as fp:
        content = fp.read()
        if decoder:
            return decoder(content)
        else:
            return content
