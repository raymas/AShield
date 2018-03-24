#
# Telemetry
#
# UART     RX     TX     CTS     RTS     Device
# UART1 P9_26     P9_24     P9_20     P9_19     /dev/ttyO1
# https://learn.adafruit.com/setting-up-io-python-library-on-beaglebone-black/uart
# requir dtc

import serial
import Adafruit_BBIO.UART as UART
import json
import logging
import time


class Telemetry(object) :
    """Default AShield Telemetry class"""

    def __init__(self) :
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='[%d/%m/%y - %H:%M:%S]')
        self.logger = logging.getLogger(__name__)

        self.logger.debug("Opening UART1...")
        UART.setup("UART1")
        self.logger.debug("UART1 is open")

        self.logger.debug("Openning serial ttyO1 at 57600 bps, see documentation")
        self.telemetrySerial = serial.Serial(port = "/dev/ttyO1", baudrate=57600)

        self.logger.debug("Closing tricks...")
        self.telemetrySerial.close()

        time.sleep(1)
        self.telemetrySerial.open()

        self.logger.debug("Serial telemetry is ready")

        return super(Telemetry, self).__init__()


    def send(self, messageDict) :
        """Use to send message. Usage : telemetry.send("{"abc":12}")"""
        if self.telemetrySerial.isOpen() :
            data = json.dumps(messageDict)
            self.logger.debug("Sending " + str(data))
            self.telemetrySerial.write(data)
        else :
            self.logger.warning("Not open")
            return 1
        return 0


    def receive(self) :
        """Use to receive message. Usage : telemetry.receive()"""
        if self.telemerySerial.isOpen() :
            received = self.telemetrySerial.readline()     # need EOL characters
        else :
            self.logger.debug("Not open could not received")
        return received
#-----------------------------------------------------------------------

if __name__ == "__main__" :
    telem = Telemetry()
    msg = {"id" : "geiger", "payload" : "20mS", "checksum" : 0x1578}
    telem.send(msg)
