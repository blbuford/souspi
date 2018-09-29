class AnovaDevice():
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
            #self.device = self.device.withDelegate(AnovaDelegate())
            #self.service = self.device.getServiceByUUID("FFE0")
            #self.characteristic = self.service.getCharacteristics()[0]
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
            #self.device.disconnect()
            self.isConnected = False

    def sendCommand(self, command):
        self.characteristic.write("{}\r".format(command))
        _, result = self.read()
        return result.rstrip()

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
        self._targetTemp = temp
        return "{}".format(self._targetTemp)

    def getCurrentTemp(self):
        return self._currentTemp

    # -- Unmocked below --
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