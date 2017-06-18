def isword(ch):
    return ch.isalnum() or ch == '.'


class State(object):
    def __init__(self):
        self._state = self._between
        self._stack = []

    def apply(self, ch):
        before = self._state
        self._state = self._state(ch)
        return not stack and before != self._between

    def _between(self, ch):
        if isword(ch):
            return self.word

        if ch == '{':
            self.stack.push(ch)
            return self._object

        if ch == '[':
            self.stack.push(ch)
            return self._object
