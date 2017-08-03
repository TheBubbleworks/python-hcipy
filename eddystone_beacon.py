#!/usr/bin/python

# An extension of the le_advertisement_test.py example for creating Physical Web (Eddystone) beacons.

from signal import pause
from sys import argv

from le_advertisement_test import BluetoothLEAdvertisementTest

class EddystoneBeaconTest(BluetoothLEAdvertisementTest):

    # -------------------------------------------
    # Eddystone  (pretty much as-is from the Google source)
    # see: https://github.com/google/eddystone/blob/master/eddystone-url/implementations/PyBeacon/PyBeacon/PyBeacon.py

    schemes = [
        "http://www.",
        "https://www.",
        "http://",
        "https://",
    ]

    extensions = [
        ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",
        ".com", ".org", ".edu", ".net", ".info", ".biz", ".gov",
    ]

    def encodeurl(self, url):
        i = 0
        data = []

        for s in range(len(EddystoneBeaconTest.schemes)):
            scheme = EddystoneBeaconTest.schemes[s]
            if url.startswith(scheme):
                data.append(s)
                i += len(scheme)
                break
        else:
            raise Exception("Invalid url scheme")

        while i < len(url):
            if url[i] == '.':
                for e in range(len(EddystoneBeaconTest.extensions)):
                    expansion = EddystoneBeaconTest.extensions[e]
                    if url.startswith(expansion, i):
                        data.append(e)
                        i += len(expansion)
                        break
                else:
                    data.append(0x2E)
                    i += 1
            else:
                data.append(ord(url[i]))
                i += 1

        return data

    def eddystone_url_adv_data(self, url):
        encodedurl = self.encodeurl(url)
        encodedurlLength = len(encodedurl)

        if encodedurlLength > 18:
            raise Exception("Encoded url too long (max 18 bytes)")

        message = [
                0x02,   # Flags length
                0x01,   # Flags data type value
                0x1a,   # Flags data

                0x03,   # Service UUID length
                0x03,   # Service UUID data type value
                0xaa,   # 16-bit Eddystone UUID
                0xfe,   # 16-bit Eddystone UUID

                5 + len(encodedurl), # Service Data length
                0x16,   # Service Data data type value
                0xaa,   # 16-bit Eddystone UUID
                0xfe,   # 16-bit Eddystone UUID

                0x10,   # Eddystone-url frame type
                0xed,   # txpower
                ]

        message += encodedurl

        return bytearray(message)


if __name__ == "__main__":

    beacon_url = argv[1] if len(argv) > 1 else "https://www.thebubbleworks.com/"

    print("Don't forget to stop the bluetoothd service, e.g: sudo service bluetooth stop\n")
    print("Beacon URL = {}".format(beacon_url))

    ebt = EddystoneBeaconTest()
    ebt.start()

    ebt.set_advertise_enable(False)

    ebt.set_advertising_parameter()

    adv_data = ebt.eddystone_url_adv_data(beacon_url)
    ebt.set_advertising_data(adv_data)

    ebt.set_advertise_enable(True)

    try:
        pause()
    except KeyboardInterrupt:
        ebt.set_advertising_data()
        ebt.set_advertise_enable(False)