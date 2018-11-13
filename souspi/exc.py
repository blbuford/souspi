class TemperatureOutOfRangeException(Exception):
    """"
    Thrown when setting a temperature that's out of the acceptable range for an Anova sous vide device
    """


class DeviceNotRunningException(Exception):
    """"
    Thrown when the device needs to be running in order to call a specific method
    """


class DeviceNotConnectedException(Exception):
    """"
    Thrown when the device is not connected to the RPI
    """