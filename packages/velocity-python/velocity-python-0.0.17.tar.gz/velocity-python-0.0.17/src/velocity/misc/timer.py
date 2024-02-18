import time


class Timer:
    def __init__(self, label='Timer'):
        self._label = label
        self.start()

    def start(self):
        self._end = self._start = time.time()
        self._diff = 0

    def end(self):
        self._end = time.time()
        self._diff = self._end - self._start

    def __str__(self):
        if not self._diff:
            self.end()
        return f"{self._label}: {self._diff:.4f} s"


if __name__ == '__main__':
    t = Timer("My Label")
    time.sleep(.003)
    time.sleep(3)
    print(t)
