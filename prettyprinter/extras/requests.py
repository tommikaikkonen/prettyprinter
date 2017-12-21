from collections import OrderedDict

from requests import Request, Response
from requests.structures import CaseInsensitiveDict

from prettyprinter import pretty_call, comment, register_pretty


MAX_CONTENT_CHARS = 500


def pretty_headers(headers, ctx):
    return pretty_call(ctx, CaseInsensitiveDict, dict(headers.items()))


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
            kwargs.append(('json', data))

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


def install():
    register_pretty(CaseInsensitiveDict)(pretty_headers)
    register_pretty(Response)(pretty_response)
