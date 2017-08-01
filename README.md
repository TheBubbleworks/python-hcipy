
# Bluetooth HCI Python library

A pure Python module written using only the Python (2.x/3.x) standard library for interacting with the Bluetooth Host Controller Interface (HCI), e.g. Bluetooth LE hardware.

The primary benefit of using this module is the lack of having any dependency on: PyBluez Python & C based module, the `bluetoothd` service or D-Bus; this module just uses the standard Python socket API.

This is being developed as an experiment for the [bluezero](https://github.com/ukBaz/python-bluezero) library in the open with the hope that developers may find it useful and might also contribute to the development.

The goal it to provide enough of the HCI API to support (at least) everything that `bluezero` aims to support, which includes:

- BLE Adapter controler and querying
- Advertisement (GATT, Eddystone Beacons, custom)
- GATT Client (Central role)
- GATT Server (Peripheral role)
- Scanning


`hcipy` could be considered to be, initially, a Python port of the [HCI support binary](https://github.com/sandeepmistry/node-bluetooth-hci-socket/blob/master/examples/le-connection-test.js) used by  NodeJS [noble](https://github.com/sandeepmistry/noble) and [bleno](https://github.com/sandeepmistry/bleno) libraries by [Sandeep Mistry](https://github.com/sandeepmistry)

The current development platform is Linux (Raspbian), although other Unix based platforms may work. Mac and Windows may be possible in the future, as they do for Noble and Bleno today, in some way.


Status:  Experimental

Author:  [Wayne Keenan](https://github.com/WayneKeenan)  / [@wkeenan](https://twitter.com/wkeenan)  of [@the_bubbleworks](https://twitter.com/the_bubbleworks)


# Examples

## HCI Device control 

The following stop/starts the `hci0` device.

[bounce_device.py](bounce_device.py)
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


## LE Scanning 

[le_scan_test.py](le_scan_test.py)

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

## LE Advertisement

An example that shows setting up Advertisement and Scan Response data.
 
[le_advertisement_test.py](le_advertisement_test.py)

## LE Connection 

An example that shows how to set up an LE connection. Contains reference information used for the `unpack`-ing of HCI packets into Python dictionaries.  

[le_advertisement_test.py](le_advertisement_test.py)


## License

Copyright (C) 2017 Wayne Keenan <wayne@thebubbleworks.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
