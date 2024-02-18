"""
Memoco-Edge Protocols
This sub-module contains every protocols classes for communicating wit hsupported edge devices.
All protocol must support a basic config-class (dataclasses) that should be validated on __init__.
Each request comes must also fulfill requirements of a Request class (inheriting from the standart Request)

ex of use :
using Class MyProtocol(IProtocol) :
    setup = {"host": ..., "port": ..., ...}
    1) validation:
        MyProtocol.from_config({}) -> ok if MyProtocolSetup(**setup) don't throw error.
    2) usage:
        request = {"type": ..., "address":..., "type": int/float/..., ...}
        MyProtocol.request(request) -> return values if MyProtocol.MyRequest(**request) don't thorw error.


"""
__version__ = "1.0.1.2"
__author__ = "Delhaye Adrien"


from iot_protocols._base import IBasicProtocol
from iot_protocols.iec62056 import *
from iot_protocols.modbus import *
from iot_protocols.snap7 import *


