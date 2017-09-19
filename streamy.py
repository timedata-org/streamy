import io, json, platform, re

"""
Emit a stream of valid JSON from a seekable file pointer like you'd get from
open or io.StringIO.

See https://stackoverflow.com/a/44190177/43839
"""

# Before Python 3.6, you need to parse the error thrown to get the character
# position. A typical error thrown looks like
#
#   ValueError: Extra data: line 1 column 4 - line 1 column 6 (char 3 - 5)

_MATCH_EXTRA_DATA_ERROR = re.compile(r'Extra data: .*char (\d+).*').match


if platform.python_version_tuple()[0] == '3':
    def to_stream(fp):
        return io.StringIO(fp) if isinstance(fp, str) else fp

else:
    def to_stream(fp):
        if isinstance(fp, unicode):  # noqa: F821
            return io.StringIO(fp)

        if isinstance(fp, str):
            return io.StringIO(unicode(fp))  # noqa: F821

        return fp


def _get_end_pos(e):
    try:
        return e.pos
    except AttributeError:
        pass

    try:
        match = _MATCH_EXTRA_DATA_ERROR(e.args[0])
        return int(match.group(1))
    except:
        pass


def _stream_with_seek(fp, kwds):
    start_pos = 0
    while True:
        # Skip whitespace
        while True:
            ch = fp.read(1)
            if not ch:
                return
            if not ch.isspace():
                fp.seek(start_pos)
                break
            start_pos += 1

        try:
            yield json.load(fp, **kwds)
            return
        except ValueError as e:
            end_pos = _get_end_pos(e)
            if end_pos is None:
                raise

            fp.seek(start_pos)
            json_str = fp.read(end_pos)
            obj = json.loads(json_str, **kwds)
            start_pos += end_pos
            yield obj


def _stream_without_seek(fp, kwds):
    buf = ''
    # XXX: alternatively could read a limited size buffer
    for l in fp:
        buf += l
        while buf:
            try:
                obj = json.loads(buf, **kwds)
            except ValueError as exc:
                end_pos = _get_end_pos(exc)
                if end_pos is None:
                    if (not exc.msg.startswith('Expecting value') or
                            buf.strip()):
                        raise

                    # buf is all whitespace
                    buf = ''
                    continue

                obj = json.loads(buf[:exc.pos])
                buf = buf[exc.pos:]
            else:
                buf = ''
            yield obj
    if buf:
        raise ValueError('Extra data!')


def stream(fp, json_lines=False, **kwds):
    """
    A function generating a stream of valid JSON objects.

    Args:
        fp: a file stream like you'd get from `open()` or `io.StringIO()`,
            or a string.
        json_lines: if true, each line holds at most one JSON expression.
        kwds: keywords to pass to json.load or json.loads.
    """
    fp = to_stream(fp)

    if json_lines:
        for i in fp:
            i = i.strip()
            if i:
                yield json.loads(i, **kwds)
        return

    if hasattr(fp, 'seek'):
        func = _stream_with_seek
    else:
        func = _stream_without_seek

    for obj in func(fp, kwds):
        yield obj
