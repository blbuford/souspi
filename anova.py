'''

BlueTooth LE Constants
Local name: Anova
Service UUID: FFE0
Characteristic UUID: FFE1
'''

from bluepy import btle
import time

class AnovaDelegate(btle.DefaultDelegate):

    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.notifications = []

    def handleNotification(self, cHandle, data):
        self.notifications.append((cHandle, data))
        self.notifications = self.notifications[-10:]

    def getLastNotification(self):
        return self.notifications[-1]


class AnovaDevice():
    def __init__(self, address):
        self.isConnected = False
        self.isRunning = False
        self.address = address
        self.device = None
        self.connect()
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

    def sendCommand(self, command):
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
        result = self.sendCommand("status")
        return result

    def start(self):
        result = self.sendCommand("start")
        self.isRunning = True
        return result

    def stop(self):
        result = self.sendCommand("stop")
        self.isRunning = False
        return result

    # Temperature Methods
    def getUnits(self):
        result = self.sendCommand("read unit")
        return result

    def setUnits(self, units):
        result = self.sendCommand("set unit {}".format(units))
        return result

    def getTargetTemp(self):
        result = self.sendCommand("read set temp")
        return result

    def setTargetTemp(self, temp):
        result = self.sendCommand("set temp {}".format(temp))
        return result

    def getCurrentTemp(self):
        result = self.sendCommand("read temp")
        return result

    # Timer Methods
    def getTimer(self):
        result = self.sendCommand("read timer")
        return result

    def setTimer(self, time):
        result = self.sendCommand("set timer {}".format(time))
        return result

    # Device must be running before this works
    def startTimer(self):
        if not self.isRunning:
            raise Exception(("Dude, you cant start a timer without starting "
                            "the device first. Call start() then this!"))
        result = self.sendCommand("start time")
        return result

    def stopTimer(self):
        result = self.sendCommand("stop time")
        return result

    # Doesnt work
    def clearAlarm(self):
        result = self.sendCommand("clear alarm")
        return result


if __name__ == "__main__":
    dev = AnovaDevice("78:A5:04:29:1E:C3")
    dev.getVersion()
    dev.disconnect()
