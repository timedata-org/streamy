#!/usr/bin/env python

import argparse, json, platform, re, sys

"""
Emit a stream of valid JSON from a seekable file pointer like you'd get from
open or io.StringIO.

See https://stackoverflow.com/a/44190177/43839
"""

_IS_PY3 = platform.python_version() >= '3'
_STRING_TYPES = str if _IS_PY3  else (str, unicode)  # noqa: F821
_PARSE_EXCEPTIONS = platform.python_version() >= '3.4'

# When we get an exception parsing a possibly-incomplete stream of JSON,
# there are two cases:
#
#   1. we don't have enough data yet to generate a complete JSON object, or
#   2. the data so far is already malformed, and requesting more won't help.
#
# json's exception doesn't give us enough information here so we have to parse
# the exception text.
#
# The rule that evolved to recognize case 1:

# "Not enough data" exception messages that start with 'Expecting', and the
# character position that they identify has to be right after the last character
# in the buffer.

# "Unterminated string" messages of any type.

_MATCH_EXPECTING_EXCEPTION = re.compile(r'Expecting .*: .*char (\d+).*').match


def stream(fp, chunk_size=0, max_message_size=0, **kwds):
    """
    A function generating a stream of valid JSON objects.

    Args:
        fp: a file stream like you'd get from `open()` or `io.StringIO()`,
            or a string.
        json_lines: if true, each line holds at most one JSON expression.
        kwds: keywords to pass to json.load or json.loads.
    """
    def yield_chunks():
        while True:
            chunk = fp.read(chunk_size)
            if not chunk:
                return
            yield chunk

    if isinstance(fp, _STRING_TYPES):
        chunks = [fp]
    elif chunk_size:
        chunks = yield_chunks()
    else:
        chunks = fp

    decoder = json.JSONDecoder(**kwds)
    unread = ''
    for chunk in chunks:
        unread = ((unread + chunk) if unread else chunk).lstrip()
        if max_message_size and len(unread) > max_message_size:
            raise ValueError('Message size exceeded max_message_size')

        while unread:
            try:
                data, index = decoder.raw_decode(unread)
            except ValueError as e:
                if not _PARSE_EXCEPTIONS:
                    # In Python 2, we just don't get enough information in
                    # the exception to figure out if we're in case 2.
                    break
                match = _MATCH_EXPECTING_EXCEPTION(e.args[0])
                if match and int(match.group(1)) >= len(unread) - 2:
                    break
                if e.args[0].startswith('Unterminated string'):
                    break

                # We're in case 2.
                raise
            else:
                yield data
                unread = unread[index:].strip()

    if unread:
        raise ValueError('Extra text at end of stream')


def _write_input_to_output(args):
    objects = 0
    try:
        with (open(args.output, 'w') if args.output else sys.stdout) as output:
            with (open(args.input) if args.input else sys.stdin) as input:
                for i in stream(input, args.chunk_size, args.max_message_size):
                    json.dump(i, output)
                    output.write('\n')
                    objects += 1
    finally:
        sys.stderr.write('JSON object writes: %s\n' % objects)


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'input', nargs='?', help='Input filename.  If none, use stdin')

    parser.add_argument(
        'output', nargs='?', help='Output filename.  If none, use stdout')

    parser.add_argument(
        '-c', '--chunk_size', default=0, type=int,
        help='Size of chunks to read from stream.  If 0, use readline.')

    parser.add_argument(
        '-m', '--max_message_size', default=0, type=int,
        help='Maximum byte size of valid messages or 0 for no maximum.')

    return parser.parse_args(sys.argv[1:])


if __name__ == '__main__':
    _write_input_to_output(_parse_args())
