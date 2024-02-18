from __future__ import annotations

from typing import Iterator

from ._constants import PREFIX


class Error:
    def __init__(self, row: int, col: int, code: int, text: str):
        self.row = row
        self.col = col
        self.code = code
        self.text = text

    @property
    def message(self) -> str:
        return '{prefix}{code}: {text}'.format(
            prefix=PREFIX,
            code=self.code,
            text=self.text,
        )

    def __iter__(self) -> Iterator[int | str]:
        yield self.row
        yield self.col
        yield self.message

    def __str__(self) -> str:
        return self.message

    def __repr__(self):
        return '{name}({content!r})'.format(
            name=type(self).__name__,
            content=self.__dict__,
        )
