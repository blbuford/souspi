#!/usr/bin/env python
from bluepy import btle
import binascii


def dump_services(dev):
    services = sorted(dev.services, key=lambda s: s.hndStart)
    for s in services:
        if s.hndStart == s.hndEnd:
            continue
        chars = s.getCharacteristics()
        for i, c in enumerate(chars):
            props = c.propertiesToString()
            if 'READ' in props:
                val = c.read()
                if c.uuid == btle.AssignedNumbers.device_name:
                    string = '\'' + \
                        val.decode('utf-8') + '\''
                elif c.uuid == btle.AssignedNumbers.device_information:
                    string = repr(val)
                else:
                    string = '<s' + binascii.b2a_hex(val).decode('utf-8') + '>'
            else:
                string = ''
            if 'Anova' in string:
                print ("%s, MAC: %s" % (string, dev.addr))


class ScanAnova(btle.DefaultDelegate):

    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.rssi < -128:
            return


def main():
    btle.Debugging = False
    scanner = btle.Scanner(0).withDelegate(ScanAnova())
    devices = scanner.scan(4)

    for d in devices:
        if not d.connectable or d.rssi < -128:
            continue

        try:
            dev = btle.Peripheral(d)
            dump_services(dev)
            dev.disconnect()
        except btle.BTLEException:
            continue


if __name__ == "__main__":
    main()
