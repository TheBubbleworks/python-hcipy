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


# -------------------------------------------------
# Socket HCI transport API

# This socket based to the Bluetooth HCI.

# Strong candidate for refactoring into factory pattern to support
# alternate transports (e.g. serial) and easier mocking for automated testing.

class BluetoothHCISocketProvider:

    def __init__(self, device_id=0):
        self.device_id = device_id
        self._keep_running = True
        self._socket = None
        self._socket_on_data_user_callback = None
        self._socket_poll_thread = None
        self._socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_RAW, socket.BTPROTO_HCI)


    def __del__(self):
        self._keep_running = False


    def open(self):

        # TODO: specify channel: HCI_CHANNEL_RAW, HCI_CHANNEL_USER, HCI_CHANNEL_CONTROL
        # https://www.spinics.net/lists/linux-bluetooth/msg37345.html
        self._socket.bind((self.device_id,))

        self._socket_poll_thread = threading.Thread(target=self._socket_poller, name='HCISocketPoller')
        self._socket_poll_thread.setDaemon(True)
        self._socket_poll_thread.start()

    def close(self):
        self._socket.close()

    def send_cmd(self, cmd, data):
        arr = array.array('B', data)
        fcntl.ioctl(self._socket.fileno(), cmd, arr)
        return arr

    def send_cmd_value(self, cmd, value):
        fcntl.ioctl(self._socket.fileno(), cmd, value)

    def write_buffer(self, data):
        self._socket.send(data)

    def set_filter(self, data):
        self._socket.setsockopt(socket.SOL_HCI, socket.HCI_FILTER, data)

    def _socket_poller(self):
        while self._keep_running:
            data = self._socket.recv(1024)         # blocking
            if self._socket_on_data_user_callback:
                self._socket_on_data_user_callback(bytearray(data))

    def on_data(self, callback):
        self._socket_on_data_user_callback = callback


class BluetoothHCI:

    def __init__(self, device_id=0, auto_start = True):
        # TODO: be given a provider interface from a factory (e.g. socket, serial, mock)
        self.hci = BluetoothHCISocketProvider(device_id)
        if auto_start:
            self.start()

    # -------------------------------------------------
    # Public HCI API, simply delegates to the composite HCI provider

    def start(self):
        self.hci.open()

    def stop(self):
        self.hci.close()

    def send_cmd(self, cmd, data):
        return self.hci.send_cmd(cmd, data)
        # packet type struct : https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n117
        # typedef struct {
        #   uint16_t	opcode;		/* OCF & OGF */
        #   uint8_t		plen;
        #   } __attribute__ ((packed))	hci_command_hdr;
        # Op-code (16 bits): identifies the command:
        #    OGF (Op-code Group Field, most significant 6 bits);
        #    OCF (Op-code Command Field, least significant 10 bits)."""

    def send_cmd_value(self, cmd, value):
        self.hci.send_cmd_value(cmd, value)

    def write(self, data):
        self.hci.write_buffer(data)

    def set_filter(self, data):
        self.hci.set_filter(data)

    def on_data(self, callback):
        self.hci.on_data(callback)

    # -------------------------------------------------
    # Public HCI Convenience API

    def device_up(self):
        self.send_cmd_value(HCIDEVUP, self.hci.device_id)

    def device_down(self):
        self.send_cmd_value(HCIDEVDOWN, self.hci.device_id)

    def get_device_info(self):

        # C hci_dev_info struct defined at https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n2382
        hci_dev_info_struct = struct.Struct('=H 8s 6B L B 8B 3L 4I 10L')

        request_dta = hci_dev_info_struct.pack(
            self.hci.device_id,
            b'',
            0, 0, 0, 0, 0, 0,
            0,
            0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0,
            0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        response_data = self.send_cmd(HCIGETDEVINFO, request_dta)

        hci_dev_info = hci_dev_info_struct.unpack(response_data)

        # Just extract a few parts for now
        device_id = hci_dev_info[0]
        device_name = hci_dev_info[1].split(b'\0',1)[0]
        bd_addr = "%0x:%0x:%0x:%0x:%0x:%0x" % hci_dev_info[7:1:-1]

        return dict(id=device_id,
                    name=device_name,
                    addr=bd_addr)


