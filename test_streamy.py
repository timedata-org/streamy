import json, streamy, unittest, io


class StreamyTest(unittest.TestCase):
    def assert_stream(self, s, *expected):
        self.assertEqual(list(streamy.stream(s)), list(expected))
        s = streamy.to_stream(s)
        try:
            delattr(s, 'seek')
        except:
            return
        self.assertEqual(list(streamy.stream(s)), list(expected))

    def stream_fails(self, s):
        try:
            list(streamy.stream(s))
        except ValueError:
            return
        raise Exception

    def test_empty(self):
        for s in '', ' ', '   ', '\n \n ':
            self.assert_stream(s)

    def test_reserved(self):
        RESERVED = {'true': True, 'false': False, 'null': None, '12': 12}
        for k, v in RESERVED.items():
            self.assert_stream(k, v)
        self.assert_stream('null false true 12.5', None, False, True, 12.5)

    def test_objects(self):
        self.assert_stream('{} {"foo": 1, "bar": true}',
                           {}, {"foo": 1, "bar": True})

    def test_lists(self):
        self.assert_stream(' [   ]    ["foo", 1, "bar", null]  ',
                           [], ["foo", 1, "bar", None])

    def test_file(self):
        with open('test_file.txt') as fp:
            self.assert_stream(fp, {'a': 'b'}, {'c': 'd'})

    def test_error(self):
        self.stream_fails(']')
        self.stream_fails('[}')
        self.stream_fails('}')
        self.stream_fails('2,,')
        self.stream_fails('[2,]')
