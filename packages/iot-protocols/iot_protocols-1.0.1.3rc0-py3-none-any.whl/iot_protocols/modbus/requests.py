
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReadCoils:
    address: int
    count: int = field(default=1)
    unit: int = field(default=1)


@dataclass
class WriteCoils:
    address: int
    values: list
    unit: int = field(default=1)


@dataclass
class ReadDiscreteInput:
    address: int
    count: int = field(default=1)
    unit: int = field(default=1)


@dataclass
class ReadHoldingRegister:
    address: int
    count: int = field(default=1)
    unit: int = field(default=1)
    encoding: str = field(default="int16")


@dataclass
class ReadInputRegister:
    address: int
    count: int = field(default=1)
    unit: int = field(default=1)
    encoding: str = field(default="bool")


@dataclass
class WriteRegister:
    address: int
    values: list
    unit: int = field(default=1)
