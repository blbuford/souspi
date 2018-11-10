"""
BlueTooth LE Constants
Local name: Anova
Service UUID: FFE0
Characteristic UUID: FFE1
"""

from bluepy import btle
import time
import exc


class AnovaDelegate(btle.DefaultDelegate):

    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.notifications = []

    def handleNotification(self, cHandle, data):
        self.notifications.append((cHandle, data))
        self.notifications = self.notifications[-10:]

    def getLastNotification(self):
        return self.notifications[-1]


class AnovaDevice:
    def __init__(self, address):
        self.isConnected = False
        self.isRunning = False
        self.address = address
        self.device = None
        self.service = None
        self.characteristic = None
        self.connect()
        self._units = self.getUnits()
        if self.isConnected:
            if 'running' in self.getStatus():
                self.isRunning = True
        else:
            raise Exception("You screwed up! This thing no connect-y.")

    def connect(self):
        try:
            self.device = btle.Peripheral(self.address)
            self.device = self.device.withDelegate(AnovaDelegate())
            self.isConnected = True
            self.service = self.device.getServiceByUUID("FFE0")
            self.characteristic = self.service.getCharacteristics()[0]
        except btle.BTLEException as err:
            print err

    def disconnect(self):
        if self.isConnected:
            self.device.disconnect()
            self.isConnected = False

    def send_command(self, command):
        try:
            self.characteristic.write("{}\r".format(command))
        except btle.BTLEException as err:
            if err.DISCONNECTED == 1:
                self.attemptReconnect(err)
                self.characteristic.write("{}\r".format(command))
            else:
                raise err
        _, result = self.read()
        return result.rstrip()

    def read(self):
        if self.device.waitForNotifications(1.0):
            return self.device.delegate.getLastNotification()
        return None

    def attemptReconnect(self, error):
        self.isConnected = False

        for i in range(3):
            self.connect()

            if not self.isConnected:
                time.sleep(3)
            else:
                break
        if not self.isConnected:
            raise Exception("Unable to reconnect to device")



    # System and general methods
    def getStatus(self):
        result = self.send_command("status")
        return result

    def start(self):
        result = self.send_command("start")
        self.isRunning = True
        return result

    def stop(self):
        result = self.send_command("stop")
        self.isRunning = False
        return result

    # Temperature Methods
    def getUnits(self):
        result = self.send_command("read unit")
        return result

    def setUnits(self, units):
        result = self.send_command("set unit {}".format(units))
        return result

    def getTargetTemp(self):
        result = self.send_command("read set temp")
        return result

    def setTargetTemp(self, temp):
        if self._units == 'f' and (temp < 32.0 or temp > 210.0):
            raise exc.TemperatureOutOfRangeException("Temperature is expected to be with 32.0 to 210.0. {} was given.".format(temp))

        result = self.send_command("set temp {}".format(temp))
        return result

    def getCurrentTemp(self):
        result = self.send_command("read temp")
        return result

    # Timer Methods
    def getTimer(self):
        result = self.send_command("read timer")
        return result

    def setTimer(self, time):
        result = self.send_command("set timer {}".format(time))
        return result

    # Device must be running before this works
    def startTimer(self):
        if not self.isRunning:
            raise Exception(("Dude, you cant start a timer without starting "
                            "the device first. Call start() then this!"))
        result = self.send_command("start time")
        return result

    def stopTimer(self):
        result = self.send_command("stop time")
        return result

    # Doesnt work
    def clearAlarm(self):
        result = self.send_command("clear alarm")
        return result

