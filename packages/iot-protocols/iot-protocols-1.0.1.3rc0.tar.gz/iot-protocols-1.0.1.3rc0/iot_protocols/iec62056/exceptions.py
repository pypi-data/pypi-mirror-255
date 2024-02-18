class MeterIdentificationFailed(Exception):
    """ Raised when the identification phase didn't worked. """


class IEC62056RequestException(Exception):
    """ Raised when a wronf request is asked"""


class SerialPortBusyException(Exception):
    """ Raised when the serial port is already in used"""