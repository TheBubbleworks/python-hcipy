#!/usr/bin/python

from signal import pause
from hcipy import *
from codecs import encode, decode

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

    def on_data(self, data):
        data = bytearray(data)
        print("on_data")
        if data[0] == HCI_EVENT_PKT:
            print("HCI_EVENT_PKT")
            if data[1] == EVT_CMD_COMPLETE:
                print("EVT_CMD_COMPLETE")

                if (data[5]<<8) + data[4] == LE_SET_ADVERTISING_PARAMETERS_CMD:
                    if data[6] == HCI_SUCCESS:
                        print('LE Advertising Parameters Set');

                elif (data[5]<<8 + data[4]) ==  LE_SET_ADVERTISING_DATA_CMD:
                    if data[6] == HCI_SUCCESS:
                        print('LE Advertising Data Set')
                elif data[5]<<8 + data[4] ==  LE_SET_SCAN_RESPONSE_DATA_CMD:
                    if data[6] == HCI_SUCCESS:
                        print('LE Scan Response Data Set')
                elif data[5]<<8 + data[4] ==  LE_SET_ADVERTISE_ENABLE_CMD:
                    if data[6] == HCI_SUCCESS:
                        print('LE Advertise Enable Set')
            elif data[1] == EVT_DISCONN_COMPLETE:
                print("EVT_DISCONN_COMPLETE")
                disconn_info = dict(
                    status = data[3],
                    handle = data[5]<<8 + data[4],
                    reason = data[6]
                )
                print(disconn_info)
                exit(0)
            elif data[1] == EVT_LE_META_EVENT:
                print("EVT_LE_META_EVENT")
                if data[3] == EVT_LE_CONN_COMPLETE:

                    conn_info = dict(
                        status= data[4],
                        handle= data[6]<<8 + data[5],
                        role=   data[7],
                        peerBdAddrType= data[8],
                        peerBdAddr= 0, #data.slice(9, 15)
                        interval=  data[16]<<8 + data[15],
                        latency= data[18]<<8 + data[17],
                        supervisionTimeout= data[20]<<8 + data[19],
                        masterClockAccuracy = data[21]
                    )
                    print(conn_info)
                    self.set_advertise_enable(True);
                elif data[3] == EVT_LE_CONN_UPDATE_COMPLETE:

                    conn_info = dict(
                        status = data[4],
                        handle = data[6]<<8 + data[5],
                        interval = data[8]<<8 + data[7],
                        latency = data[10]<<8 + data[9],
                        supervisionTimeout = data[12]<<8 + data[11],
                    )
                    print(conn_info)


if __name__ == "__main__":

    print("Please stop the bluetoothd service: sudo service bluetooth stop")
    ble_advertise_test = BluetoothLEAdvertisementTest()

    scan_rsp_data = decode(b'0909657374696d6f74650e160a182eb8855fb5ddb601000200', 'hex')
    adv_data = decode(b'0201061aff4c000215b9407f30f5f8466eaff925556b57fe6d00010002b6', 'hex')

    ble_advertise_test.set_filter()
    ble_advertise_test.start()

    ble_advertise_test.set_advertise_enable(False)

    ble_advertise_test.set_advertising_parameter()
    ble_advertise_test.set_scan_response_data(scan_rsp_data)
    ble_advertise_test.set_advertising_data(adv_data)

    ble_advertise_test.set_advertise_enable(True)

    pause()



