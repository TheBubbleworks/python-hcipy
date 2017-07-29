#!/usr/bin/python
from os import popen
from hcipy import *


# Functionally equivalent to:

# $ sudo hciconfig hci0 down
# $ sudo hciconfig hci0 up

hci = BluetoothHCI(0)
hci.start()

print(hci.get_device_info())

hci.device_down()
print(popen("hciconfig").read())

hci.device_up()
print(popen("hciconfig").read())
