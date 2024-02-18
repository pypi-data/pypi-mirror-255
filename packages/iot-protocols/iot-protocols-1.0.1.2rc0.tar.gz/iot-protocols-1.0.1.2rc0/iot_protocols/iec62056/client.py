from __future__ import annotations
from dataclasses import dataclass, field
import time
"""
? Author : Delhaye Adrien
IEC 62056 (serial/tcp) module.
This module allows to exchange data using the IEC62056 protocol over a serial line.
* How to use : 
    1) create a client : client = IEC62056Client(baudrate=xxx, device_address="xxx", port="xxx")
    2) client.connect()
    3) read all or registers : client.read_all() | client.read_registers(registers = ["1.8.0", "2.8.0"])
"""
import logging
import serial

from typing import List

from iec62056 import client, messages, constants, exceptions

from iot_protocols.iec62056.exceptions import *
from iot_protocols._base import IBasicProtocol


IEC62056_REACTION_TIME = 1.5 # Maximum reaction time for IEC62056


@dataclass
class TariffResponse:
    data: List[messages.DataSet]
    bcc: bytes
    checked: bool = field(default=False)

    def __repr__(self) -> str:
        return f"Tariff Response (number of datasets : {len(self.data)})(bcc: {self.checked})"

    def get_register(self, address: str) -> messages.DataSet:
        for dataset in self.data:
            if dataset.address == address:
                return dataset


class IEC62056Client(IBasicProtocol):
    
    """Class to communicate with meter using IEC62056-21 protocol.
    Usage:
    - Create a new client specifying it's baudrate, the port, if needed the meter address (serial number, ..) and the type of client (serial, tcp (encapsulated), ..).
    - To request all dataset available use client.read_all()
    - To request a particular register use client.read_registers(list_of_registers_by_obis_code).

    Returns:
        client : A new instance of a IEC62056 client's.
    """
    BAUDRATE_CHAR = {
        300: "0",
        600: "1",
        1200: "2",
        2400: "3",
        4800: "4",
        9600: "5",
        19200: "6"
    }

    def __init__(
            self,
            baudrate: int,
            port: str,
            transport: str,
            parity: str,
            bytesize: int,
            stopbits: int,
            **kwargs):
        
        self._baudrate = baudrate
        self._port = port
        self._parity = parity
        self._bytesize = bytesize
        self._stopbits = stopbits

        if transport == "serial":
            self._client: client.Iec6205621Client = client.Iec6205621Client.with_serial_transport(
                port=self._port,
                device_address=""
            )

            self._client.transport.TRANSPORT_REQUIRES_ADDRESS = True

        elif transport == "tcp":
            #TODO: to be implemented.
            raise NotImplementedError("This feature is not implemented yet.")

        else:
            self.disconnect()
            raise ValueError(f"Type : {type} is not valid.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(baudrate : {self._baudrate} | port: {self._port} | {self._parity} | {self._bytesize} | {self._stopbits})"
    
    @property
    def baudrate(self) -> int:
        try:
            return self._client.transport.port.baudrate
        except AttributeError:
            return "undefined"
    
    def connect(self):
        try:
            if not self._is_connected():
                self._client.connect()
            
            self._client.transport.port.baudrate = self._baudrate

        except serial.serialutil.SerialException as err:
            raise SerialPortBusyException(f"The serial port {self._port} is not available : {err}")
        
    def _is_connected(self) -> bool:
        if self._client.transport.port is not None:
            return self._client.transport.port.is_open
        return False
    
    def disconnect(self):
        self._client.disconnect()

    def request(self, meter_address: str="", table: int=0, timeout: int = 10) -> TariffResponse:
        """read_registers specified in the list for the requested table of the iec62056-21 meter.

        Args:
            registers (list, optional): list of registers obis code to read. Defaults to [].
            table (str, optional): table to be read. Defaults to 0 which is equivalent to a standart readout.

        Returns:
            List[messages.DataSet]: A list of Dataset element that contains the requested registers if found.
        """
        try:
            self.connect()
        except SerialPortBusyException as err:
            raise err

        try:
            logging.debug(f"[Meter.Identification] Start Identification Message.")
            identification = self.read_tariff_identification(meter_address=meter_address)
            logging.debug(f"[Meter.Identification] Meter Identification has been read : {identification}")
            
            self.send_ack_message(table=table)

            logging.debug(f"[Meter.ACK.Sent] ACK message.")
            response: TariffResponse = self.read_tariff_response(timeout=timeout)
            logging.debug(f"[Meter.Data.Received] Response from tariff device : {response!r}")

            self.disconnect()

            return response

        except Exception as err:
            self.disconnect()
            raise IEC62056RequestException(f"Could not read registers : {err}")

    def read_tariff_identification(self, device_address: str="", timeout: int=5):
        try:
            request = messages.RequestMessage(device_address=device_address)
            logging.debug(f"[Identification.Request] Sending identification request: {request}.")
            self.connect()
            self._client.transport.send(request.to_bytes())

            # Wait to ensure the tariff device has time to responds.
            self._client.rest(IEC62056_REACTION_TIME)

            response = self._client.read_identification()
            if isinstance(response, messages.IdentificationMessage):
                logging.debug(f"[Identification.Response] Received : {response}")
                return response
            else:
                raise MeterIdentificationFailed(f"Cannot communicate with the meter using: baudrate: {self.baudrate} | parity: {self._parity} | bytesize: {self._bytesize} | stopbits: {self._stopbits}.")
        
        except Exception as err:
            raise IEC62056RequestException(f"Cannot read meter identification message : {err}")
    
    def _get_ack_message(self, table: int=0) -> messages.AckOptionSelectMessage:
        message = messages.AckOptionSelectMessage(
            baud_char=self.BAUDRATE_CHAR[self._baudrate],
            mode_char=table
        )

        return message

    def send_ack_message(self, table: int=0) -> None:
        message = self._get_ack_message(table)
        data = message.to_bytes()
        self._client.transport.send(data)
        self._client.rest(IEC62056_REACTION_TIME)

    @staticmethod
    def check_bcc(data: bytes, bcc: bytes) -> bool:
        if not isinstance(data, bytes) or not isinstance(bcc, bytes) or len(bcc) != 1:
            raise ValueError("Input must be bytes and bcc must be a single byte")
        x = b'\x00'[0]
        for b in data[1:]:
            x = x^b

        logging.debug(f"[BCC.Check] received({bcc[0]}) | computed({x})")
        return x == bcc[0]

    def read_tariff_response(self, timeout: int = 10) -> TariffResponse:
        result = []
        port: serial.Serial = self._client.transport.port
        port.timeout = timeout
        encoded = port.read_until(constants.ETX.encode())
        bcc = port.read(1)
        bcc_checked = self.check_bcc(encoded, bcc)

        logging.debug(f"[Meter.ReadTariffResponse.Received] Received {len(encoded)} bytes (bcc: {bcc}).")

        lines = encoded.decode().split('\r\n')

        for line in lines:
            try:
                # The first line contains STX character that can be removed for decoding first register.
                if line.startswith(constants.STX):
                    line = line.replace(constants.STX, '')

                if line.startswith(constants.ETX):
                    line = line.replace(constants.ETX, '')
              
                try:
                    dataset = messages.DataSet.from_representation(line)
                    result.append(dataset)
                except exceptions.Iec6205621ParseError:
                    pass
                
            except Exception as err:
                logging.warning(f"Could not decode dataset for line : {err}")

        return TariffResponse(
            data=result,
            bcc=bcc,
            checked=bcc_checked
        )
    