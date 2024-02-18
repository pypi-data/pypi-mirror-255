from labdevices.exceptions import CommunicationError_ProtocolViolation, CommunicationError_Timeout, CommunicationError_NotConnected
from labdevices.scpi import SCPIDeviceEthernet

from time import sleep

import atexit

class Agilent34410A:
    def __init__(
        self,
        address = None,
        port = 5025,
        logger = None
    ):
        self._scpi = SCPIDeviceEthernet(address, port, logger)

        self._usedConnect = False
        self._usedContext = False

        atexit.register(self.__close)

    def _connect(self, address = None, port = None):
        if self._scpi.connect():
            v = self._id()

        return True

    def _disconnect(self):
        self._scpi.disconnect()
    def _isConnected(self):
        return self._scpi.isConnected()

    def __enter__(self):
        if self._usedConnect:
            raise ValueError("Cannot use context management on already connected device")
        self._connect()
        self._usesContext = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__close()
        self._usesContext = False

    def __close(self):
        atexit.unregister(self.__close)
        self._disconnect()

    def _id(self):
        res = self._scpi.scpiQuery("*IDN?")
        res = res.split(",")
        if len(res) != 4:
            raise CommunicationError_ProtocolViolation("IDN string does not follow Agilents layout")
        if res[0] != "Agilent Technologies":
            raise CommunicationError_ProtocolViolation(f"IDN returned manufacturer {res[0]}")
        if res[1] != "34410A":
            raise CommunicationError_ProtocolViolation(f"IDN did not return device type 34410A but {res[1]}")
        return {
            'type' : res[1],
            'serial' : res[2]
        }
    def _serial(self):
        return self._id()['serial']

    def _get_voltage(self):
        resp = self._scpi.scpiCommand(":CONF:VOLT:DC")
        resp = self._scpi.scpiQuery(":READ?")
        return resp

    def _get_current(self):
        resp = self._scpi.scpiCommand(":CONF:CURR:DC")
        resp = self._scpi.scpiCommand(":READ?")
        return resp

if __name__ == "__main__":
    with Agilent34410A("10.4.1.14") as multi:
        print(multi._get_voltage())
