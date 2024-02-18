import logging
from snap7.client import Client
from snap7 import util

from iot_protocols import IBasicProtocol
from iot_protocols.snap7.requests import *


class S7Decoder:
    _decoding_map={
        "bool": util.get_bool,
        "byte": util.get_byte,
        "int": util.get_int,
        "real": util.get_real,
        "string": util.get_string,
        "date": util.get_date
    }
    @classmethod
    def get_decoder(cls, type: str) -> callable:
        try:
            return cls._decoding_map[type]
        except KeyError as err:
            logging.error(f"Type :{type} not in decoder.")


class S7Client(IBasicProtocol):
    """
    Client for communication with S7 controller.
    The requests parameters must be a mapping of all the data that should be retrieved. For exemple there is an request exemple for 3 different type of values:
    request:{
        "Temperature":{
            "offset": 0,
            "type": "real",
        },
        "Username":{
            "offset": 4,
            "type": "string",
        },
        "WindStrength":{
            "offset": 262,
            "type": "real"
        }
    }
    should return a dict with the key that will be Temperature, Username, WindStrength and their respsective value will be the value read.
    """
    def __init__(self, host: str, rack: int=0, slot: int=1, port: int=102) -> None:
        self._host = host
        self._rack = rack
        self._slot = slot
        self._port = port
        self._client = Client()

    def __enter__(self):
        self.connect()
    
    def __exit__(self):
        self.disconnect()

    @property
    def host(self) -> str:
        return self._host
    
    @property
    def rack(self) -> int:
        return self._rack
    
    @property
    def slot(self) -> int:
        return self._slot

    @property
    def port(self) -> int:
        return self._port
    
    def connect(self):
        self._client.connect(self._host, self._rack, self._slot, self._port)

    def disconnect(self):
        self._client.disconnect()

    async def read_datablock(self, request: dict):
        """ The reading of the datablock must done knowing the total bytesize of the datablock part to read. Then all the data are return based on they decoding.
        """
        try:
            req = ReadDatablockRequest(**request)
            result = self._read_datablock(req)
            
        except TypeError as err:
            logging.error(f"Wrong parameters for read_datablock : {err}. Ensure the request fir the ReadDatablockRequest schema")

    def _read_datablock(self, request: ReadDatablockRequest):
        pass
    
    def _write_datablock(self, request: WriteDataBlockRequest):
        pass