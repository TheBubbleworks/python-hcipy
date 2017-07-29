#!/usr/bin/python
from signal import pause
from hcipy import *

# based on: https://github.com/sandeepmistry/node-bluetooth-hci-socket/blob/master/examples/le-scan-test.js

class BluetoothLEScanTest:

    def __init__(self, dev_id=0):
        self.hci = BluetoothHCI(dev_id)
        self.hci.on_data(self.on_data)
        self.hci.start()
        print(self.hci.get_device_info())

    def __del__(self):
        self.hci.on_data(None)
        self.hci.stop()


    def set_filter(self):
        typeMask   = 1 << HCI_EVENT_PKT
        eventMask1 = (1 << EVT_CMD_COMPLETE) | (1 << EVT_CMD_STATUS)
        eventMask2 = 1 << (EVT_LE_META_EVENT - 32)
        opcode     = 0

        filter = struct.pack("<LLLH", typeMask, eventMask1, eventMask2, opcode)
        self.hci.set_filter(filter)

    def set_scan_parameters(self):
        len = 7
        type = SCAN_TYPE_ACTIVE
        internal = 0x0010   #  ms * 1.6
        window = 0x0010     #  ms * 1.6
        own_addr  = LE_PUBLIC_ADDRESS
        filter = FILTER_POLICY_NO_WHITELIST
        cmd = struct.pack("<BHBBHHBB", HCI_COMMAND_PKT, LE_SET_SCAN_PARAMETERS_CMD, len,
                          type, internal, window, own_addr, filter )

        self.hci.write(cmd)


    def set_scan_enable(self, enabled=False, duplicates=False):
        len = 2
        enable = 0x01 if enabled else 0x00
        dups   = 0x01 if duplicates else 0x00
        cmd = struct.pack("<BHBBB", HCI_COMMAND_PKT, LE_SET_SCAN_ENABLE_CMD, len, enable, dups)
        self.hci.write(cmd)


    # receives a bytearray
    def on_data(self, data):
        if ord(data[0]) == HCI_EVENT_PKT:
            print("HCI_EVENT_PKT")
            if ord(data[1]) == EVT_CMD_COMPLETE:
                print("EVT_CMD_COMPLETE")

                if (ord(data[5])<<8) + ord(data[4]) == LE_SET_SCAN_PARAMETERS_CMD:
                    if ord(data[6]) == HCI_SUCCESS:
                        print('LE Scan Parameters Set');

                elif (ord(data[5])<<8 + ord(data[4])) ==  LE_SET_SCAN_ENABLE_CMD:
                    if ord(data[6]) == HCI_SUCCESS:
                        print('LE Scan Enable Set')

            elif ord(data[1]) == EVT_LE_META_EVENT:
                print("EVT_LE_META_EVENT")
                if ord(data[3]) == EVT_LE_ADVERTISING_REPORT:
                    # TODO: check offsets for all of these:

                    gap_adv_type =['ADV_IND', 'ADV_DIRECT_IND', 'ADV_SCAN_IND', 'ADV_NONCONN_IND', 'SCAN_RSP'][ord(data[5])]
                    gap_addr_type = ['PUBLIC', 'RANDOM'][ord(data[6])]
                    gap_addr =  [hex(ord(c)) for c in data[12:6:-1]]
                    eir = [chr(ord(c)) for c in data[14:-2]]
                    rssi = ord(data[-1])

                    print('LE Advertising Report')
                    print('\tAdv Type  = {}'.format(gap_adv_type))
                    print('\tAddr Type = {}'.format(gap_addr_type))
                    print('\tAddr      = {}'.format(gap_addr))
                    print('\tEIR       = {}'.format(eir))
                    print('\tRSSI      = {}'.format(rssi))


if __name__ == "__main__":

    ble_scan_test = BluetoothLEScanTest()

    ble_scan_test.set_scan_enable(False)
    ble_scan_test.set_filter()
    ble_scan_test.set_scan_parameters()
    ble_scan_test.set_scan_enable(True, True)

    pause()