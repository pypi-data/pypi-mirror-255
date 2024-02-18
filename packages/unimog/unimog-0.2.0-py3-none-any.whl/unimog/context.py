from dataclasses import dataclass
from typing import Optional, Self


@dataclass(kw_only=True)
class Context:
    def __init__(self):
        self._error = None
        self._is_success = None

    def __post_init__(self):
        self._is_success: bool = True
        self._error: Optional[str] = None

    def failure(self, error_message: str) -> Self:
        self._error = error_message
        self._is_success = False

        return self

    def success(self) -> Self:
        self._is_success = True

        return self

    def is_failure(self) -> bool:
        return not self._is_success

    def is_success(self) -> bool:
        return self._is_success

    @property
    def error(self):
        return self._error
