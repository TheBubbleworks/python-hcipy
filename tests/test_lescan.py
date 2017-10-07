import unittest
from time import sleep

MICROBIT1_BD_ADDR='0xf5:0x3a:0xc9:0xb0:0x15:0xf6'

SCANTIME = 5            # seconds

from .le_scan_test import BluetoothLEScanTest

class TestLEScan(unittest.TestCase):

    def test_lescan_find_microbit1(self):
        ble_scan_test = BluetoothLEScanTest()

        ble_scan_test.set_scan_enable(False)
        ble_scan_test.set_filter()
        ble_scan_test.set_scan_parameters()
        ble_scan_test.set_scan_enable(True, True)

        sleep(SCANTIME)

        ble_scan_test.set_scan_enable(False)

        self.assertTrue(MICROBIT1_BD_ADDR in ble_scan_test.found_bd_addrs)


