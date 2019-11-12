from typing import Optional, Generic, TypeVar

T = TypeVar("T")


class Result(Generic[T]):
    def __init__(self, success: bool, value: Optional[T], error: Optional[str] = None):
        self.success = success
        self.value = value
        self.error = error

    def __repr__(self):
        return f"Result(success={self.success}, value={self.value}, error={self.error})"
