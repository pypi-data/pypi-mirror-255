from atlantiscore.db.types.evm.base import ByteEncoding
from atlantiscore.types.evm import (
    EVMTransactionHash as PythonTransactionHash,
    LiteralByteEncoding,
)

PRECISION = 79


class EVMTransactionHash(ByteEncoding):
    _precision: int = PRECISION

    @staticmethod
    def _parse(
        value: PythonTransactionHash | LiteralByteEncoding,
    ) -> PythonTransactionHash:
        return PythonTransactionHash(value)
