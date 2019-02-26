from datetime import timedelta
from io import BytesIO
from requests import (
    Request,
    Response,
    Session,
)
from requests.structures import CaseInsensitiveDict

from prettyprinter import (
    install_extras,
    pformat,
)

install_extras(['requests'])


def test_session():
    sess = Session()
    sess.auth = ('user', 'pass')
    assert pformat(sess, width=999) == """\
requests.Session(
    headers=requests.structures.CaseInsensitiveDict({
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'User-Agent': 'python-requests/2.21.0'
    }),
    auth=('user', 'pass')
)"""


def test_request():
    request = Request(
        'GET',
        'https://example.com/pages/1',
        data={'ok': True},
        headers={
            'Content-Type': 'application/json',
        }
    )
    assert pformat(request, width=999) == """\
requests.Request(
    method='GET',
    url='https://example.com/pages/1',
    data={'ok': True},
    headers={'Content-Type': 'application/json'}
)"""


def test_prepared_request():
    request = Request(
        'POST',
        'https://example.com/pages/1',
        json={'a': ['b', 'c', 'd']},
        headers={
            'Content-Type': 'application/json',
        }
    )
    prepped = request.prepare()
    assert pformat(prepped, width=999) == """\
requests.PreparedRequest(
    method='POST',
    url='https://example.com/pages/1',
    headers=requests.structures.CaseInsensitiveDict({
        'Content-Length': '22',
        'Content-Type': 'application/json'
    }),
    body=b'{"a": ["b"'  # ... and 12 more bytes
)"""


def test_response():
    request = Request(
        'POST',
        'https://example.com/pages/1',
        json={'a': ['b', 'c', 'd']},
        headers={
            'Content-Type': 'application/json',
        }
    )
    prepped = request.prepare()

    payload = 'This is the response body.'.encode('utf-8')
    resp = Response()
    resp.raw = BytesIO(payload)
    resp.request = prepped
    resp.status_code = 200
    resp.url = 'https://example.com/pages/1'
    resp.encoding = 'utf-8'
    resp.reason = 'OK'
    resp.elapsed = timedelta(seconds=2)
    resp.headers = CaseInsensitiveDict({
        'Content-Type': 'text/plain',
        'Content-Length': len(payload)
    })
    assert pformat(resp, width=999) == """\
# Response content not loaded yet
requests.Response(
    status_code=200,  # OK
    url='https://example.com/pages/1',
    elapsed=datetime.timedelta(seconds=2),
    headers=requests.structures.CaseInsensitiveDict({
        'Content-Length': 26,
        'Content-Type': 'text/plain'
    })
)"""

    # Loads content
    resp.text

    assert pformat(resp, width=999) == """\
requests.Response(
    url='https://example.com/pages/1',
    status_code=200,  # OK
    elapsed=datetime.timedelta(seconds=2),
    headers=requests.structures.CaseInsensitiveDict({
        'Content-Length': 26,
        'Content-Type': 'text/plain'
    }),
    text='This is the response body.'
)"""
