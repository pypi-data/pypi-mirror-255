from dataclasses import dataclass


@dataclass
class ReadDatablockRequest:
    db_number: int
    start: int
    size: int


@dataclass
class WriteDataBlockRequest:
    db_number: int
    start: int
    data: bytearray