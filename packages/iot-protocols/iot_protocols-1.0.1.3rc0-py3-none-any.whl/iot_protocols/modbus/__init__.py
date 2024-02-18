from iot_protocols.modbus.client import ModbusClient
from iot_protocols.modbus.exceptions import ModbusConfigurationException



def create_client(configuration: dict) -> ModbusClient:
    if configuration["transport"] == "serial":
        return ModbusClient.with_serial_client(**configuration)
    
    elif configuration["transport"] == "tcp":
        return ModbusClient.with_tcp_client(**configuration)
    
    else:
        raise ModbusConfigurationException(f"Invalid configuration for Modbus protocol.")