
# This experiment is no longer being maintained, development focus has moved to the cross platform [bleson](https://github.com/TheCellule/python-bleson) library.

# Bluetooth HCI Python library   

A pure Python module written using only the Python (2.x/3.x) standard library for interacting with the Bluetooth Host Controller Interface (HCI), e.g. for controlling Bluetooth LE hardware.

The primary benefit of using this module is the lack of having any dependency on: the PyBluez Python (& C based) module, the `bluetoothd` service or D-Bus; this module just uses the standard Python socket API.

This is being developed as an experiment for the [bluezero](https://github.com/ukBaz/python-bluezero) library in the open with the hope that developers may find it useful and might also contribute to the development.

The ultimate goal is to provide easy access to enough of the HCI API to support (at least) everything that `bluezero` aims to support, which includes:

- BLE Adapter controler and querying
- Advertisement (GATT, Eddystone Beacons, custom)
- GATT Client (Central role)
- GATT Server (Peripheral role)
- Scanning


`hcipy` could be considered to be, initially, a Python port of the [HCI support binary](https://github.com/sandeepmistry/node-bluetooth-hci-socket/blob/master/examples/le-connection-test.js) used by  NodeJS [noble](https://github.com/sandeepmistry/noble) and [bleno](https://github.com/sandeepmistry/bleno) libraries by [Sandeep Mistry](https://github.com/sandeepmistry)

The current development platform is Linux (Raspbian), although other Unix based platforms may work. Mac and Windows may be possible in the future, as they do for Noble and Bleno today, in some way.


Status:  __Experimental__ - currently a low-level HCI wrapper with a handful of examples for context and usage.

Author:  [Wayne Keenan](https://github.com/WayneKeenan)  / [@wkeenan](https://twitter.com/wkeenan)  of [@the_bubbleworks](https://twitter.com/the_bubbleworks)

---

# Getting Started

Running the following on a freshly setup Pi running Raspbian Jessie (or Jessie Lite) will turn your Pi into a Physical Web (Eddystone) beacon:

```bash
git clone https://github.com/TheBubbleworks/python-hcipy && cd python-hcipy

sudo service bluetooth stop
sudo python eddystone_beacon.py
```

You can also provide your own URL for the beacon as a parameter:
```bash
sudo python eddystone_beacon.py https://raspberrypi.org/
```


 You can install the `hcipy` library using `pip` if you wish:

 ```bash
 sudo pip install hcipy
 ```

Considering the early stage of `hcipy` development the value of doing so is probably very limited and you will still need to clone/copy the examples from the `hcipy` github repo.

---

# Examples

The examples demonstrate different low level use cases for communicating with the Bluetooth HCI API using `hcipy`.  The functionality that they excersise will be wrapped up into higher level functions in this library or a seperate library.

Before running a `hcipy` based script you should stop the `bluetoothd` system service (as it can interfer):
```bash
sudo service bluetooth stop
```

By default `hcipy` scripts need to be run as `root` user to allow access the kernel's HCI interface, e.g.:
```
sudo python eddystone_beacon.py
```

This restriction can be removed, please see below.


## Example 1 - HCI Device control 

The following stop/starts the `hci0` device,   [bounce_device.py](tests/bounce_device.py).
```python
from hcipy import *

hci = BluetoothHCI(0)
hci.start()
hci.device_down()
hci.device_up()
```


Which is functionally identical to:
```bash
$ sudo hciconfig hci0 down
$ sudo hciconfig hci0 up
```


## Example 2 - LE Scanning 

Scan for Bluetooth LE devices, [le_scan_test.py](tests/le_scan_test.py).

```python
ble_scan_test = BluetoothLEScanTest()
ble_scan_test.set_scan_enable(False)
ble_scan_test.set_filter()
ble_scan_test.set_scan_parameters()
ble_scan_test.set_scan_enable(True, True)
```

'Screenshot' of output:

```bash
sudo python le_scan_test.py 
{'id': 0, 'name': 'hci0', 'addr': 'b8:27:eb:45:12:b5'}
HCI_EVENT_PKT
EVT_CMD_COMPLETE
HCI_EVENT_PKT
EVT_CMD_COMPLETE
LE Scan Parameters Set
HCI_EVENT_PKT
EVT_CMD_COMPLETE
HCI_EVENT_PKT
EVT_LE_META_EVENT
LE Advertising Report
	Adv Type  = ADV_IND
	Addr Type = RANDOM
	Addr      = ['0xf4', '0x58', '0x8e', '0x30', '0x7b', '0x43']
	EIR       = ['\x02', '\x01', '\x05', '\r', '\t', 'P', 'u', 'c', 'k', '.', 'j', 's', ' ', '7', 'b', '4']
	RSSI      = 178
```

## Example 3 - LE Advertisement

An example that shows setting up Advertisement and Scan Response data, [le_advertisement_test.py](tests/le_advertisement_test.py).


## Example 4 - Physical Web Beacon (Eddystone)

An example that demonstrates a Physical Web (Eddystone) beacon, [eddystone_beacon.py](tests/eddystone_beacon.py)


## Example 5 - LE Connection

An example that shows how to set up an LE connection, [le_connection_test.py](tests/le_connection_test.py).

Contains reference information used for the `unpack`-ing of HCI packets into Python dictionaries.


---

# Restrictions


The requirement to run as the `root` user can be removed by running the following commands just once (or after any Python upgrade):

```bash
sudo setcap cap_net_raw+eip $(eval readlink -f `which python`)
sudo setcap cap_net_raw+eip $(eval readlink -f `which python3`)
```

on Stretch:

```bash
sudo setcap cap_net_raw,cap_net_admin+eip $(eval readlink -f `which python`)
sudo setcap cap_net_raw,cap_net_admin+eip $(eval readlink -f `which python3`)
```

Note 1: Some may consider this to be a potential security risk (TODO: elaborate), but it's handy :)

Note 2: For the minority of users that boot from an NFS mounted root filesystem please be aware that `setcap` won't work for you. You can ignore this if you use the normal method of booting off an SDCard.



---

## License

Copyright (C) 2017 Wayne Keenan <wayne@thebubbleworks.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
