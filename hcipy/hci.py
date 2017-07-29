#!/usr/bin/python

# Bluetooth HCI Python library  (Experimental)
#
# Pure Python and standard library based module for interacting with the Bluetooth HCI.
# There is no dependency on the PyBluez Python/Native libraries, bluetoothd service or D-Bus.

# This can be considered to be a Pythonisation of the NodeJS NoBLE/ BLENo by Sandeep Mistry.

# Author:  Wayne Keenan
# email:   wayne@thebubbleworks.com
# Twitter: https://twitter.com/wkeenan


# Acknowledgements:

# Significant information taken from https://github.com/sandeepmistry/node-bluetooth-hci-socket
# With help from https://github.com/colin-guyon/py-bluetooth-utils and the BlueZ Python library.

import array
import struct
import fcntl
import socket
import threading

from .constants import *

class BluetoothHCI:

    def __init__(self, dev_id=0):
        self.dev_id = dev_id
        self._keep_running = True
        self._socket = None
        self._socket_on_data_user_callback = None
        self._socket_poll_thread = None

    def __del__(self):
        self._keep_running = False

    # -------------------------------------------------
    # Private HCI transport communication API

    # This is the single interface between the BluetoothHCI methods and the HCI transport.

    # Strong candidate for refactoring into a 'provider interface' pattern to support
    # alternate transports (e.g. serial) and easier mocking for automated testing.

    def _hci_open(self):
        self._socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)
        self._socket.bind((self.dev_id,))

        self._socket_poll_thread = threading.Thread(target=self._socket_poller, name='HCISocketPoller')
        self._socket_poll_thread.setDaemon(True)
        self._socket_poll_thread.start()

    def _hci_close(self):
        self._socket.close()

    def _hci_send_cmd(self, cmd, data):
        arr = array.array('B', data)
        fcntl.ioctl(self._socket.fileno(), cmd, arr)
        return arr

    def _hci_send_cmd_value(self, cmd, value):
        fcntl.ioctl(self._socket.fileno(), cmd, value)

    def _hci_write_buffer(self, data):
        self._socket.send(data)

    def _hci_set_filter(self, data):
        self._socket.setsockopt(socket.SOL_HCI, socket.HCI_FILTER, data)

    def _socket_poller(self):
        while self._keep_running:
            data = self._socket.recv(1024)         # blocking
            if self._socket_on_data_user_callback:
                self._socket_on_data_user_callback(data) # bytearray

    # -------------------------------------------------
    # Public HCI API

    def start(self):
        self._hci_open()

    def stop(self):
        self._hci_close()

    def write(self, data):
        self._hci_write_buffer(data)

    def set_filter(self, data):
        self._hci_set_filter(data)

    def on_data(self, callback):
        self._socket_on_data_user_callback = callback

    # -------------------------------------------------
    # Public HCI Convenience API

    def device_up(self):
        self._hci_send_cmd_value(HCIDEVUP, self.dev_id)

    def device_down(self):
        self._hci_send_cmd_value(HCIDEVDOWN, self.dev_id)

    def get_device_info(self):

        # `struct hci_dev_info` defined at https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n2382
        s = struct.Struct('=H 8s 6B L B 8B 3L 4I 10L')

        request_dta = s.pack(
            self.dev_id,
            '',
            0, 0, 0, 0, 0, 0,
            0,
            0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        response_data = self._hci_send_cmd(HCIGETDEVINFO, request_dta)

        hci_dev_info = s.unpack(response_data)

        # Just extract a few parts for now
        device_id = hci_dev_info[0]
        device_name = hci_dev_info[1].split(b'\0',1)[0]
        bd_addr = "%0x:%0x:%0x:%0x:%0x:%0x" % hci_dev_info[7:1:-1]

        return dict(id=device_id,
                    name=device_name,
                    addr=bd_addr)


