from abc import ABCMeta, abstractmethod
from decimal import Decimal
from typing import Optional, TypeVar

from sqlalchemy.engine import Dialect
from sqlalchemy.sql.sqltypes import Numeric
from sqlalchemy.types import NUMERIC, TypeDecorator, TypeEngine

from atlantiscore.types.evm import (
    ByteEncoding as PythonByteEncoding,
    LiteralByteEncoding,
)

T = TypeVar("T", bound=PythonByteEncoding)


class ByteEncoding(TypeDecorator, metaclass=ABCMeta):
    impl: TypeEngine = NUMERIC
    cache_ok: bool = True
    _precision: int

    def load_dialect_impl(self, dialect: Dialect) -> Numeric:
        return dialect.type_descriptor(NUMERIC(self._precision))

    def process_bind_param(
        self,
        value: Optional[T | LiteralByteEncoding],
        dialect: Dialect,
    ) -> int:
        if value is None:
            return value
        return int(self._parse(value))

    def process_result_value(
        self,
        value: Optional[int | Decimal],
        dialect: Dialect,
    ) -> T:
        if value is None:
            return value
        return self._parse(int(value))

    @staticmethod
    @abstractmethod
    def _parse(value: T | LiteralByteEncoding) -> T:
        """Parses value to T."""
