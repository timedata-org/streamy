import json, re

# Before Python 3.6, you need to parse the error thrown to get the character
# position. A typical error thrown looks like
#
#   ValueError: Extra data: line 1 column 4 - line 1 column 6 (char 3 - 5)

_MATCH_EXTRA_DATA_ERROR = re.compile(r'Extra data: .*\(char (\d+).*\)').match


def stream_read_json(stream):
    start_pos = 0
    while True:
        try:
            obj = json.load(stream)
            yield obj
            return
        except ValueError as e:
            try:
                end_pos = e.pos
            except AttributeError:
                end_pos = None

            if end_pos is None:
                match = _MATCH_EXTRA_DATA_ERROR(e.args[0])
                if not match:
                    raise
                end_pos = int(match.group(1))

            stream.seek(start_pos)
            json_str = stream.read(end_pos)
            obj = json.loads(json_str)
            start_pos += end_pos
            yield obj
