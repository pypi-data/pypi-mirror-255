import logging
import time
import pytest
from iot_protocols.iec62056.client import IEC62056Client, TariffResponse
from iec62056 import messages


METER_ADDRESS="5987893"
PORT="COM3"
BAUDRATE=19200
PARITY="E"
BYTESIZE=7
STOPBITS=1
TYPE="serial"

@pytest.fixture
def client() -> IEC62056Client:
    return IEC62056Client(
        baudrate=BAUDRATE,
        port=PORT,
        transport=TYPE,
        parity=PARITY,
        bytesize=BYTESIZE,
        stopbits=STOPBITS
    )


def test_read_identification(client: IEC62056Client):
    response = client.read_tariff_identification(
        METER_ADDRESS,
        timeout=5
    )
    assert isinstance(response, messages.IdentificationMessage)
    logging.info(f"Idenfication from meter : {response}")
    time.sleep(10) # Wait to not conflict with further request.

def test_read_default_table(client: IEC62056Client):
    response = client.request(METER_ADDRESS) 
    assert isinstance(response, TariffResponse)
    assert response.checked == True
    logging.info(f"Response : {response!r}")
    line_char = "\r\n"
    logging.info(f"{line_char.join([str(dataset) for dataset in response.data])}")
    time.sleep(10) # Wait to not conflict with further request.


def test_read_energy_table(client: IEC62056Client):
    response = client.request(METER_ADDRESS, table=7) 
    assert isinstance(response, TariffResponse)
    assert response.checked == True
    logging.info(f"Response : {response!r}")
    line_char = "\r\n"
    logging.info(f"{line_char.join([str(dataset) for dataset in response.data])}")
