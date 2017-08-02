#!/usr/bin/python

# An extension of the le_advertisement_test for Physical Web (Eddystone) beacons.

from signal import pause
from sys import argv
from hcipy import *


class EddystoneBeaconTest:

    def __init__(self, device_id=0):
        self.hci = BluetoothHCI(device_id, auto_start=False)
        self.hci.start()
        self.hci.device_down()
        self.hci.device_up()

    def __del__(self):
        self.hci.stop()

    def set_advertise_enable(self, enabled):
        cmd = struct.pack("<BHB" + "B",
                          HCI_COMMAND_PKT,
                          LE_SET_ADVERTISE_ENABLE_CMD,
                          1,  # cmd parameters length
                          0x01 if enabled else 0x00
                          )
        self.hci.write(cmd)

    def set_advertising_parameters(self):
        cmd = struct.pack("<BHB" + "2H 3B 6B B B",
                          HCI_COMMAND_PKT,
                          LE_SET_ADVERTISING_PARAMETERS_CMD,
                          15,  # cmd parameters length
                          0x00a0,  # min interval
                          0x00a0,  # max interval
                          0,  # adv type
                          0,  # direct addr type
                          0,  # direct addr type
                          0, 0, 0, 0, 0, 0,  # direct addr
                          0x07,
                          0x00
                          )
        self.hci.write(cmd)


    def set_advertising_data(self, data=b''):
        #  Pad unused bytes in the advertisment with 0
        padded_data = memoryview(data).tolist()
        padded_data.extend([0] * (31 - len(padded_data)))

        cmd = struct.pack("<BHB" + "B 31B",
                          HCI_COMMAND_PKT,
                          LE_SET_ADVERTISING_DATA_CMD,
                          32,  # cmd parameters length
                          len(data),
                          *padded_data
                          )
        self.hci.write(cmd)


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

    ebt.set_advertise_enable(False)

    ebt.set_advertising_parameters()

    adv_data = ebt.eddystone_url_adv_data(beacon_url)
    ebt.set_advertising_data(adv_data)

    ebt.set_advertise_enable(True)

    try:
        pause()
    except KeyboardInterrupt:
        ebt.set_advertising_data()
        ebt.set_advertise_enable(False)