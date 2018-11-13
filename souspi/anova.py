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

    def last_notification(self):
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
        self._units = self.get_units()
        if self.isConnected:
            if 'running' in self.status():
                self.isRunning = True
        else:
            raise Exception("You screwed up! This thing no connect-y.")

    def connect(self):
        self.device = btle.Peripheral(self.address)
        self.device = self.device.withDelegate(AnovaDelegate())
        self.isConnected = True
        self.service = self.device.getServiceByUUID("FFE0")
        self.characteristic = self.service.getCharacteristics()[0]

    def disconnect(self):
        if self.isConnected:
            self.device.disconnect()
            self.isConnected = False

    def send_command(self, command):
        if self.characteristic is None:
            raise exc.DeviceNotConnectedException("The Bluetooth characteristic is None. Try calling connect()")
        try:
            self.characteristic.write("{}\r".format(command))
        except btle.BTLEException as err:
            if err.DISCONNECTED == 1:
                self.attempt_reconnect()
                self.characteristic.write("{}\r".format(command))
            else:
                raise err
        _, result = self.read()
        return result.rstrip()

    def read(self):
        if self.device.waitForNotifications(1.0):
            return self.device.delegate.last_notification()
        return None

    def attempt_reconnect(self):
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
    def status(self):
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
    def get_units(self):
        result = self.send_command("read unit")
        return result

    def set_units(self, units):
        result = self.send_command("set unit {}".format(units))
        return result

    def get_target_temp(self):
        result = self.send_command("read set temp")
        return result

    def set_target_temp(self, temp):
        if self._units == 'f' and (temp < 32.0 or temp > 210.0):
            error_msg = "Temperature is expected to be with 32.0 to 210.0. {} was given.".format(temp)
            raise exc.TemperatureOutOfRangeException(error_msg)

        result = self.send_command("set temp {}".format(temp))
        return result

    def current_temp(self):
        result = self.send_command("read temp")
        return result

    # Timer Methods
    def get_timer(self):
        result = self.send_command("read timer")
        return result

    def set_timer(self, time):
        result = self.send_command("set timer {}".format(time))
        return result

    # Device must be running before this works
    def start_timer(self):
        if not self.isRunning:
            raise exc.DeviceNotRunningException("Start the device first. Call start() then this!")
        result = self.send_command("start time")
        return result

    def stop_timer(self):
        result = self.send_command("stop time")
        return result
