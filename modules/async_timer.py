import time


class AsyncTimer:
    async def __aenter__(self):
        self.start = time.perf_counter()
        return self

    def lap(self) -> float:
        dt = time.perf_counter() - self.start
        return dt

    async def __aexit__(self, *args):
        pass
