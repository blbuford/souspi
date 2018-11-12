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
            if 'running' in self.status():
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
    def status(self):
        if self._status:
            return 'running'
        else:
            return 'stopped'

    def start(self):
        self._status = True
        self.isRunning = True
        return self.status()

    def stop(self):
        self._status = False
        self.isRunning = False
        return self.status()

    # Temperature Methods
    def get_units(self):
        return self._units

    def set_units(self, units):
        if units.lower() == 'f' or units.lower() == 'c':
            self._units = units.lower()
        else:
            raise Exception('Units given are something other than F or C')

        return self._units

    def get_target_temp(self):
        return self._targetTemp

    def set_target_temp(self, temp):
        if self._units == 'f' and (temp < 32.0 or temp > 210.0):
            error_msg = "Temperature is expected to be with 32.0 to 210.0. {} was given.".format(temp)
            raise exc.TemperatureOutOfRangeException(error_msg)

        self._targetTemp = temp
        r = "{}".format(self._targetTemp)
        print "setting target temp to {}".format(r)
        return r

    def current_temp(self):
        return self._currentTemp

    # -- Unmocked below --
    # Timer Methods
    def get_timer(self):
        return 0.0
