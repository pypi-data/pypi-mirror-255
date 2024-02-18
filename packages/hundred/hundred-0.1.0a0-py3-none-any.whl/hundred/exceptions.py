from abc import ABC

__all__ = ("Error",)


class Error[T](Exception, ABC):
    __slots__ = ("status_code", "content")

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 400,
        content: T = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.content = content or message
