
# Bluetooth HCI Python library

A pure Python module written using only the Python standard library for interacting with the Bluetooth HCI.

The primary benefit is the lack of dependency on the PyBluez Python/Native libraries, bluetoothd service and D-Bus.

`hcipy` could be considered to be a Pythonisation of the NodeJS [noble](https://github.com/sandeepmistry/noble) and [bleno](https://github.com/sandeepmistry/bleno) libraries by [Sandeep Mistry](https://github.com/sandeepmistry)

This is being developed as an experiment for the [bluezero](https://github.com/ukBaz/python-bluezero) library in the open with the hope that developers may find it useful and might also contribute to the development.


Status:  Experimental

Author:  [Wayne Keenan](https://github.com/WayneKeenan)  / [@wkeenan](https://twitter.com/wkeenan)  


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


## License

Copyright (C) 2017 Wayne Keenan <wayne@thebubbleworks.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
