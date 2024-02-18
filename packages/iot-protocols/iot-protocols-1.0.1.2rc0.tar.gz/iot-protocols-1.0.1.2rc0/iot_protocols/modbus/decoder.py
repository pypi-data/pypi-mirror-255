import logging

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from iot_protocols.modbus.exceptions import ModbusDecoderException

class ModbusPayloadDecoder:

    _functions_map = {
        "int8": BinaryPayloadDecoder.decode_8bit_int,
        "int16": BinaryPayloadDecoder.decode_16bit_int,
        "int32":BinaryPayloadDecoder.decode_32bit_int,
        "int64": BinaryPayloadDecoder.decode_64bit_int,
        "uint8": BinaryPayloadDecoder.decode_8bit_uint,
        "uint16": BinaryPayloadDecoder.decode_16bit_uint,
        "uint32": BinaryPayloadDecoder.decode_32bit_uint,
        "uint64": BinaryPayloadDecoder.decode_64bit_uint,
        "float16": BinaryPayloadDecoder.decode_16bit_float,
        "float32": BinaryPayloadDecoder.decode_32bit_float,
        "float64": BinaryPayloadDecoder.decode_64bit_float,
        "str": BinaryPayloadDecoder.decode_string,
        "string": BinaryPayloadDecoder.decode_string
    }
    @classmethod
    def decode(cls, registers, encoding):
        if encoding not in cls._functions_map:
            return registers
        
        try:
            decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Big)
            f = cls._functions_map[encoding]
            if encoding == "str" or encoding=="string":
                size = len(registers)*2 # one register (word) store 2 char
                return f(decoder, size).decode().strip("\x00")
            return f(decoder)
        except KeyError as err:
            logging.error(f"Encoding specified for decoding isn't valid : {err}.")
            raise ModbusDecoderException(f"Invalid Enconding {encoding}")
        
        except Exception as err:
            logging.error(f"Cannot decode modbus registers : {err}")
            raise ModbusDecoderException(f"Cannot decode values for encoding : {encoding} : {err}")
