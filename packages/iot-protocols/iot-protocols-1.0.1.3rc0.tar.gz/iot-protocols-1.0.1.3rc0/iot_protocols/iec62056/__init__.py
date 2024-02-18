from iot_protocols.iec62056.client import IEC62056Client


def create_client(configuration: dict) -> IEC62056Client:
    return IEC62056Client(**configuration)
