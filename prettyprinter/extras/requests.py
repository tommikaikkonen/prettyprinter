from collections import OrderedDict

from requests import (
    PreparedRequest,
    Request,
    Response,
    Session,
)
from requests.models import DEFAULT_REDIRECT_LIMIT
from requests.hooks import default_hooks
from requests.structures import CaseInsensitiveDict

from prettyprinter import pretty_call, comment, register_pretty


MAX_CONTENT_CHARS = 500


def pretty_headers(headers, ctx):
    return pretty_call(ctx, CaseInsensitiveDict, dict(headers.items()))


def pretty_request(request, ctx):
    kwargs = [
        ('method', request.method),
        ('url', request.url),
    ]

    if request.cookies:
        kwargs.append(('cookies', request.cookies))

    if request.auth:
        kwargs.append(('auth', request.auth))

    if request.json:
        kwargs.append(('json', request.json))

    if request.data:
        kwargs.append(('data', request.data))

    if request.files:
        kwargs.append(('files', request.files))

    if request.headers:
        kwargs.append(('headers', request.headers))

    if request.params:
        kwargs.append(('params', request.params))

    if request.hooks and request.hooks != default_hooks():
        kwargs.append(('hooks', request.hooks))

    return pretty_call(ctx, 'requests.Request', **OrderedDict(kwargs))


def pretty_prepared_request(request, ctx):
    kwargs = [
        ('method', request.method),
        ('url', request.url),
    ]

    if request.headers:
        kwargs.append(('headers', request.headers))

    if request.body is not None:
        count_bytes = len(request.body)

        kwargs.append((
            'body',
            comment(
                request.body[:10],
                '... and {} more bytes'.format(count_bytes - 10)
            )
        ))

    if request.hooks != default_hooks():
        kwargs.append(('hooks', request.hooks))

    return pretty_call(ctx, 'requests.PreparedRequest', **OrderedDict(kwargs))


def pretty_response(resp, ctx):
    content_consumed = bool(resp._content_consumed)

    if not content_consumed:
        return comment(
            pretty_call(
                ctx,
                'requests.Response',
                status_code=comment(resp.status_code, resp.reason),
                url=resp.url,
                elapsed=resp.elapsed,
                headers=resp.headers,
            ),
            'Response content not loaded yet'
        )

    kwargs = [
        ('url', resp.url),
        ('status_code', comment(resp.status_code, resp.reason)),
        ('elapsed', resp.elapsed),
        ('headers', resp.headers),
    ]

    has_valid_json_payload = False
    if resp.headers.get('Content-Type', 'text/plain').startswith('application/json'):
        try:
            data = resp.json()
        except ValueError:
            pass
        else:
            has_valid_json_payload = True
            kwargs.append(('json', comment(data, 'Access with .json()')))

    if not has_valid_json_payload:
        text = resp.text
        count_chars_truncated = max(0, len(text) - MAX_CONTENT_CHARS)

        if count_chars_truncated:
            truncated = text[:MAX_CONTENT_CHARS]
            kwargs.append((
                'text',
                comment(truncated, '{} characters truncated'.format(count_chars_truncated))
            ))
        else:
            kwargs.append(('text', text))

    return pretty_call(ctx, 'requests.Response', **OrderedDict(kwargs))


def pretty_session(session, ctx):
    kwargs = []

    if session.headers:
        kwargs.append(('headers', session.headers))

    if session.auth is not None:
        kwargs.append(('auth', session.auth))

    if session.params:
        kwargs.append(('params', session.params))

    if session.stream:
        kwargs.append(('stream', session.stream))

    if session.cert is not None:
        kwargs.append(('cert', session.cert))

    if session.max_redirects != DEFAULT_REDIRECT_LIMIT:
        kwargs.append(('max_redirects', session.max_redirects))

    if session.cookies:
        kwargs.append(('cookies', session.cookies))

    return pretty_call(ctx, 'requests.Session', **OrderedDict(kwargs))


def install():
    register_pretty(CaseInsensitiveDict)(pretty_headers)
    register_pretty(Response)(pretty_response)
    register_pretty(Request)(pretty_request)
    register_pretty(PreparedRequest)(pretty_prepared_request)
    register_pretty(Session)(pretty_session)
