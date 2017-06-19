def isword(ch):
    return ch.isalnum() or ch == '.'


class State(object):
    def __init__(self):
        self._state = self._between
        self._stack = []

    def apply(self, ch):
        before = self._state
        self._state = self._state(ch)
        return not self._stack and before != self._between

    def _between(self, ch):
        if isspace(ch):
            return self._between

        if ch.isnumeric():
            return self._number

        if isword(ch):
            return self._word

        if ch == '{':
            self.stack.push(ch)
            return self._object

        if ch == '[':
            self.stack.push(ch)
            return self._list

        if char == '"':
            self.stack.push(ch)
            return self._string

    def _word(self, ch):
        pass

    def _object(self, ch):
        pass

    def _list(self, ch):
        pass
