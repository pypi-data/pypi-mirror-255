import numpy as np

__all__ = ["ArrayGenerator"]


class ArrayGenerator:
    def __init__(self, size: int):
        self._size = size

    def __call__(self) -> np.ndarray[int]:
        return np.random.random(size=self._size)
