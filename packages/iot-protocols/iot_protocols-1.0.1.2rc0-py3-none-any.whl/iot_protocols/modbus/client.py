from __future__ import annotations

import logging
from typing import Any, List

from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
from pymodbus.framer import socket_framer, rtu_framer, tls_framer, ModbusFramer
from pymodbus.exceptions import ConnectionException
from multipledispatch import dispatch

from iot_protocols import IBasicProtocol
from iot_protocols.modbus.exceptions import *
from iot_protocols.modbus import requests
from iot_protocols.modbus.decoder import ModbusPayloadDecoder


MODBUS_FUNCTION_TO_CODE={
    0x01: "ReadCoils",
    0x02: "ReadDiscreteInput",
    0x03: "ReadHoldingRegister",
    0x04: "ReadInputRegister",
    0x05: "WriteCoils",
    0x06: "WriteRegister",
}


class ModbusClient(IBasicProtocol):

    def __init__(self, client):
        self._client: ModbusSerialClient | ModbusTcpClient = client

    def connect(self) -> bool:
        return self._client.connect()
    
    def disconnect(self) -> None:
        self._client.close()
    
    @dispatch(dict)
    def request(self, request: dict) -> Any:
        try:
            function = request.pop("function")
            factory = getattr(requests, function)
            return self.request(factory(**request))
        
        except (KeyError, AttributeError) as err:
            raise ModbusRequestException(f"Wrong request configuration: {err}.")
    
    @dispatch(requests.ReadCoils)
    def request(self, request: requests.ReadCoils) -> List[bool]:
        try:
            self.connect()
            _response = self._client.read_coils(**request.__dict__)
            if _response.isError():
                raise ModbusRequestException(self._get_error_message(_response, request))
            
            result =  _response.bits[:request.count]
            if request.count==1:
                return result[0]
            self.disconnect()
            return result
        
        except ConnectionException as err:
            raise ModbusClientException(f"Could not connect to modbus client : {err}")
        except TimeoutError as err:
            raise ModbusRequestException(f"Request to the modbus device timeout : {err}")
        except Exception as err:
            raise ModbusRequestException(f"Request to the modbus device failed: {err}")
    
    @dispatch(requests.WriteCoils)
    def request(self, request: requests.WriteCoils) -> List[bool]:
        try:
            self.connect()
            _request = self._client.write_coils(**request.__dict__)
            print(f"MODBUS RESPONSE ---> {_request}")
            if _request.isError():
                raise ModbusRequestException(self._get_error_message(_request, request))
            
            return self.request(requests.ReadCoils(address=request.address, count=len(request.values), unit=request.unit))
        except ConnectionException as err:
            raise ModbusClientException(f"Could not connect to modbus client : {err}")
        except TimeoutError as err:
            raise ModbusRequestException(f"Request to the modbus device timeout : {err}")
        except Exception as err:
            raise ModbusRequestException(f"Request to the modbus device failed: {err}")
        
    @dispatch(requests.ReadDiscreteInput)
    def request(self, request: requests.ReadDiscreteInput) -> List[bool]:
        try:
            self.connect()
            _response = self._client.read_discrete_inputs(**request.__dict__)
            if _response.isError():
                return ModbusRequestException(self._get_error_message(_response, request))

            result =  _response.bits[:request.count]
            if request.count==1:
                return result[0]
            self.disconnect()
            return result
        except ConnectionException as err:
            raise ModbusClientException(f"Could not connect to modbus client : {err}")
        except TimeoutError as err:
            raise ModbusRequestException(f"Request to the modbus device timeout : {err}")
        except Exception as err:
            raise ModbusRequestException(f"Request to the modbus device failed: {err}")
        
    @dispatch(requests.ReadInputRegister)
    def request(self, request: requests.ReadInputRegister) -> List[float | int | str] | float | int | str:
        try:
            self.connect()
            _response = self._client.read_input_registers(**request.__dict__)
            if _response.isError():
                return ModbusRequestException(self._get_error_message(_response, request))
            
            decoded = ModbusPayloadDecoder.decode(_response.registers, request.encoding)
            self.disconnect()
            return decoded
        
        except ConnectionException as err:
            raise ModbusClientException(f"Could not connect to modbus client : {err}")
        except TimeoutError as err:
            raise ModbusRequestException(f"Request to the modbus device timeout : {err}")
        except Exception as err:
            raise ModbusRequestException(f"Request to the modbus device failed: {err}")
        
    @dispatch(requests.ReadHoldingRegister)
    def request(self, request: requests.ReadHoldingRegister) -> List[float | int | str] | float | int | str:
        try:
            self.connect()
            _response = self._client.read_holding_registers(**request.__dict__)
            if _response.isError():
                return ModbusRequestException(self._get_error_message(_response, request))
        
            decoded = ModbusPayloadDecoder.decode(_response.registers, request.encoding)
            self.disconnect()

            return decoded
    
        except ConnectionException as err:
            raise ModbusClientException(f"Could not connect to modbus client : {err}")
        except TimeoutError as err:
            raise ModbusRequestException(f"Request to the modbus device timeout : {err}")
        except Exception as err:
            raise ModbusRequestException(f"Request to the modbus device failed: {err}")
        
    @dispatch(requests.WriteRegister)
    def request(self, request: requests.WriteRegister) -> List[float | int | str] | float | int | str:
        try:
            self.connect()
            _response = self._client.write_registers(**request.__dict__)
            if _response.isError():
                raise ModbusRequestException(self._get_error_message(_response, request))
            
            return self.request(requests.ReadHoldingRegister(address=request.address, count=len(request.values), unit=request.unit, encoding=str(type(request.values))))
        
        except ConnectionException as err:
            raise ModbusClientException(f"Could not connect to modbus client : {err}")
        except TimeoutError as err:
            raise ModbusRequestException(f"Request to the modbus device timeout : {err}")
        except Exception as err:
            raise ModbusRequestException(f"Request to the modbus device failed: {err}")
        
    def _get_error_message(self, exception, request, **kwargs) -> str:
        try:
            error_message = f"Error when executing Modbus Request from {self.__class__.__name__} with request {request} : {exception}"
            return error_message
        except Exception as err:
            logging.error(f"Could not generate error msg : {err}")
            return f"Modbus Request failed - Cannot get Error Message : {err}"

    @classmethod
    def with_serial_client(cls, port: str, method: str, baudrate: int, parity: str, stopbits: str, bytesize: str, timeout: int = 5, **kwargs):
        """ Createa a ModbusClient isntance with serial transport communication."""
        client = ModbusSerialClient(
            port=port,
            method=method,
            stopbits=stopbits,
            bytesize=bytesize,
            parity=parity,
            timeout=timeout,
            baudrate=baudrate
        )
        if isinstance(client, ModbusSerialClient):
            return cls(client)
        else:
            return ModbusClientException("Could not initiate modbus serial client")
        
    @classmethod
    def with_tcp_client(cls, host: str, port: int=502, timeout: int=10, framer: ModbusFramer = "socket", **kwargs):
        """ Create a ModbusClient instance with TCP transport communication."""

        if framer == "rtu":
            framer = rtu_framer.ModbusRtuFramer
        else:
            framer = socket_framer.ModbusSocketFramer

        client = ModbusTcpClient(
            host=host,
            port=port,
            timeout=timeout,
            framer=framer
        )
        if isinstance(client, ModbusTcpClient):
            return cls(client)
        else:
            raise ModbusClientException("Could not initiate modbus tcp client")