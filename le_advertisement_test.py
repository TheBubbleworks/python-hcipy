#!/usr/bin/python

from signal import pause
from hcipy import *

# based on: https://github.com/sandeepmistry/node-bluetooth-hci-socket/blob/master/examples/le-advertisement-test.js

class BluetoothLEAdvertisementTest():

    def __init__(self, device_id=0):
        self.hci = BluetoothHCI(device_id)


        self.hci.on_data(self.on_data)

    def __del__(self):
        self.hci.on_data(None)
        self.hci.stop()

    def start(self):
        self.hci.start()
        self.hci.device_down()
        self.hci.device_up()

    def set_filter(self):
        typeMask   = 1 << HCI_EVENT_PKT | (1 << HCI_ACLDATA_PKT)
        eventMask1 = 1 << EVT_DISCONN_COMPLETE | (1 << EVT_CMD_COMPLETE) | (1 << EVT_CMD_STATUS)
        eventMask2 = 1 << (EVT_LE_META_EVENT - 32)
        opcode     = 0

        filter = struct.pack("<LLLH", typeMask, eventMask1, eventMask2, opcode)
        self.hci.set_filter(filter)

    def set_advertise_enable(self, enabled):
        cmd = struct.pack("<BHBB",
                          HCI_COMMAND_PKT,
                          LE_SET_ADVERTISE_ENABLE_CMD,
                          1,            # cmd parameters length
                          0x01 if enabled else 0x00
                          )
        self.hci.write(cmd)


    def set_advertising_parameter(self):
        cmd = struct.pack("<BHB" + "H H 3B 6B B B",
                          HCI_COMMAND_PKT,
                          LE_SET_ADVERTISING_PARAMETERS_CMD,
                          15,           # cmd parameters length
                          0x00a0,       # min interval
                          0x00a0,       # max interval
                          0,            # adv type
                          0,            # direct addr type
                          0,            # direct addr type
                          0,0,0,0,0,0,  # direct addr
                          0x07,
                          0x00
                          )
        self.hci.write(cmd)

    def set_scan_response_data(self, data):
        padded_data = memoryview(data).tolist()
        padded_data.extend([0] * (31 - len(padded_data)))

        cmd = struct.pack("<BHB" + "B31B",
                          HCI_COMMAND_PKT,
                          LE_SET_SCAN_RESPONSE_DATA_CMD,
                          32,           # cmd parameters length
                          len(data),
                          *padded_data
                          )
        self.hci.write(cmd)

    def set_advertising_data(self, data):
        padded_data = memoryview(data).tolist()
        padded_data.extend([0] * (31 - len(padded_data)))

        cmd = struct.pack("<BHB" + "B31B",
                          HCI_COMMAND_PKT,
                          LE_SET_ADVERTISING_DATA_CMD,
                          32,           # cmd parameters length
                          len(data),
                          *padded_data
                          )
        self.hci.write(cmd)

    # receives a bytearray
    def on_data(self, data):
        print("on_data")
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

    print("Please stop the bluetoothd service: sudo service bluetooth stop")
    ble_advertise_test = BluetoothLEAdvertisementTest()

    scan_rsp_data = '0909657374696d6f74650e160a182eb8855fb5ddb601000200'
    adv_data = '0201061aff4c000215b9407f30f5f8466eaff925556b57fe6d00010002b6'

    ble_advertise_test.set_filter()
    ble_advertise_test.start()

    ble_advertise_test.set_advertise_enable(False)

    ble_advertise_test.set_advertising_parameter()
    ble_advertise_test.set_scan_response_data(scan_rsp_data.decode('hex'))
    ble_advertise_test.set_advertising_data(adv_data.decode('hex'))
    
    ble_advertise_test.set_advertise_enable(True)

    pause()



