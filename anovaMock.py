from bluepy.btle import BTLEException
from anova import TemperatureOutOfRangeException

class Characteristic:
    def write(self, txt):
        raise BTLEException(BTLEException.DISCONNECTED, "Device disconnected")


class AnovaDevice:
    def __init__(self, address):
        self.isConnected = False
        self.isRunning = False
        self.address = address
        self._status = False
        self._units = 'f'
        self._currentTemp = 100
        self._targetTemp = 130
        self.connect()
        if self.isConnected:
            # self.device = self.device.withDelegate(AnovaDelegate())
            # self.service = self.device.getServiceByUUID("FFE0")
            # self.characteristic = self.service.getCharacteristics()[0]
            if 'running' in self.getStatus():
                self.isRunning = True
        else:
            raise Exception("You screwed up! This thing no connect-y.")

    def connect(self):
        if not self.isConnected:
            self.isConnected = True
        else:
            raise Exception("You're already connected! What are you doing with your life?")

    def disconnect(self):
        if self.isConnected:
            # self.device.disconnect()
            self.isConnected = False

    def send_command(self, command):
        try:
            self.characteristic.write("{}\r".format(command))
        except BTLEException as err:
            if err.DISCONNECTED == 1:
                self.connect()
                self.characteristic.write("{}\r".format(command))
        _, result = self.read()
        return result.rstrip()

    def _fsendCommand(self, command):
        raise BTLEException(BTLEException.DISCONNECTED, "Device disconnected")

    def read(self):
        if self.device.waitForNotifications(1.0):
            return self.device.delegate.getLastNotification()
        return None

    # System and general methods
    def getStatus(self):
        if self._status:
            return 'running'
        else:
            return 'stopped'

    def start(self):
        self._status = True
        self.isRunning = True
        return self.getStatus()

    def stop(self):
        self._status = False
        self.isRunning = False
        return self.getStatus()

    # Temperature Methods
    def getUnits(self):
        return self._units

    def setUnits(self, units):
        if units.lower() == 'f' or units.lower() == 'c':
            self._units = units.lower()
        else:
            raise Exception('Units given are something other than F or C')

        return self._units

    def getTargetTemp(self):
        return self._targetTemp

    def setTargetTemp(self, temp):
        if self._units == 'f' and (temp < 32.0 or temp > 210.0):
            raise TemperatureOutOfRangeException("Temperature is expected to be with 32.0 to 210.0. {} was given.".format(temp))

        self._targetTemp = temp
        r = "{}".format(self._targetTemp)
        print "setting target temp to {}".format(r)
        return r

    def getCurrentTemp(self):
        return self._currentTemp

    # -- Unmocked below --
    # Timer Methods
    def getTimer(self):
        result = 20.3 #self.send_command("read timer")
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