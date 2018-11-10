import exc


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
            raise exc.TemperatureOutOfRangeException("Temperature is expected to be with 32.0 to 210.0. {} was given.".format(temp))

        self._targetTemp = temp
        r = "{}".format(self._targetTemp)
        print "setting target temp to {}".format(r)
        return r

    def getCurrentTemp(self):
        return self._currentTemp

    # -- Unmocked below --
    # Timer Methods
    def getTimer(self):
        return 0.0
