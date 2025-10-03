from time import perf_counter


class Timer:
    def __init__(self):
        self.start = perf_counter()

    def reset(self) -> float:
        prev = self.elapsed
        self.start = perf_counter()
        return prev

    @property
    def elapsed(self) -> float:
        return perf_counter() - self.start
