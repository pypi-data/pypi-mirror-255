from atlantiscore.db.types.evm.base import ByteEncoding
from atlantiscore.types.evm import EVMAddress as PythonEVMAddress, LiteralByteEncoding

PRECISION = 49


class EVMAddress(ByteEncoding):
    _precision: int = PRECISION

    @staticmethod
    def _parse(value: PythonEVMAddress | LiteralByteEncoding) -> PythonEVMAddress:
        return PythonEVMAddress(value)
