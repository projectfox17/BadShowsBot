import time


class AsyncTimer:

    async def __aenter__(self):
        self.start = time.perf_counter()
        return self
    
    @property
    def elapsed(self) -> float:
        delta = time.perf_counter() - self.start
        return delta

    async def __aexit__(self, *args):
        # end = time.perf_counter()
        # print(f"Task took {end - self.start:.3f} sec")
        pass
