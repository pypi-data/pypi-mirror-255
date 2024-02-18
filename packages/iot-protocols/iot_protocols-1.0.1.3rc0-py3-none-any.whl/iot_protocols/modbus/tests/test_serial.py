import logging
import pytest
from iot_protocols.modbus import create_client, ModbusClient


#! Those test are preformed on a MOXA R1248 with modbus unit 1

@pytest.fixture
def client() -> ModbusClient:
    return create_client(
        {
            "type": "Modbus",
            "transport": "serial",
            "modbus_id": 1,
            "method": "rtu",
            "port": "COM3",
            "baudrate": 9600,
            "stopbits": 1,
            "bytesize": 8,
            "parity": "N",
            "timeout": 3
        }
    )


def test_rw_coils(client: ModbusClient):
    values = [True, False, True, False, True, False]
    logging.info(f"WriteCoils -> {values}")
    _w = client.request(
        {
            "function": "WriteCoils",
            "address": 320,
            "unit": 1,
         
            "values": values
        }
    )
    _r = client.request(
        {
            "function": "ReadCoils",
            "address": 320,
            "unit": 1,
            "count": 6,
        }
    )
    logging.info(f"ReadCoils -> {_r}")
    assert _r == values

def test_r_input_register(client: ModbusClient):
    _r = client.request({
        "function": "ReadInputRegister",
        "address": 0,
        "count": 6,
        "unit": 1,
        "encoding": "bool"
    })
    assert _r is not None
    assert isinstance(_r, list) and len(_r) == 6
    logging.info(f"ReadHoldingRegister -> {_r}")


def test_r_input_register(client: ModbusClient):
    _r = client.request({
        "function": "ReadInputRegister",
        "address": 30027,
        "count": 6,
        "unit": 1,
        "encoding": "str"
    })
    assert _r is not None
    assert isinstance(_r, str) and len(_r) > 0
    logging.info(f"ReadInputRegister -> {_r}")


def test_r_profile(client: ModbusClient):
    _r = client.request({
        "function": "ReadInputRegister",
        "address": 0x7545,
        "count": 2,
        "unit": 1,
        "encoding": "str"
    })
    logging.info(f"FirmwareVersion -> {_r}")
    assert _r is not None

    _r = client.request({
        "function": "ReadInputRegister",
        "address": 0x7547,
        "count": 2,
        "unit": 1,
        "encoding": "str"
    })
    assert _r is not None
    logging.info(f"Realease Date -> {_r}")

    _r = client.request({
        "function": "ReadInputRegister",
        "address": 30026,
        "count": 1,
        "unit": 1,
    })
    assert _r is not None
    logging.info(f"Vendor ID -> {_r}")
