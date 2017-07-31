#!/usr/bin/python

from signal import pause
from codecs import decode
from pprint import pformat
from hcipy import *

# based on: https://github.com/sandeepmistry/node-bluetooth-hci-socket/blob/master/examples/le-connection-test.js

class BluetoothLEConnectionTest:

    def __init__(self, dev_id=0):
        self.hci = BluetoothHCI(dev_id, auto_start=False)
        self.hci.on_data(self.on_data)

    def __del__(self):
        self.hci.stop()

    def set_filter(self):

        filter = struct.pack(HCIPY_HCI_FILTER_STRUCT,
                             (1 << HCI_EVENT_PKT) | (1 << HCI_ACLDATA_PKT),     # Type Mask
                             (1 << EVT_DISCONN_COMPLETE)
                             | (1 << EVT_CMD_COMPLETE)
                             | (1 << EVT_CMD_STATUS),                           # eventMask1
                             1 << (EVT_LE_META_EVENT - 32),                     # eventMask1
                             0                                                  # opcode
                             )

        self.hci.set_filter(filter)


    def create_connection(self, addr, addr_type):
        bd_addr = list(reversed(bytearray.fromhex(addr.replace(':', ' '))))     # TODO: make a common utility function
        print('bd_addr={}'.format([hex(b) for b in bd_addr]))                   # TODO: make a common utility function

        cmd = struct.pack(HCIPY_HCI_CMD_STRUCT_HEADER + "HHB B 6B B 6H",
                          HCI_COMMAND_PKT,
                          LE_CREATE_CONN_CMD,
                          0x19,         # cmd parameters length
                          0x0060,       # interval
                          0x0030,       # window
                          0x00,         # initiator filter
                          addr_type,    # peer address type
                          bd_addr[0], bd_addr[1], bd_addr[2], bd_addr[3], bd_addr[4], bd_addr[5],
                          0x0000,       # own address type
                          0x0028,       # min interval
                          0x0038,       # max interval
                          0x0000,       # latency
                          0x002a,       # supervision timeout
                          0x0000,       # min ce length
                          0x0000,       # max ce length
                          )
        self.hci.write(cmd)


    def write_handle(self, handle, data):
        data_len = len(data)
        cmd = struct.pack("B 4H {}B".format(data_len),
                          HCI_ACLDATA_PKT,
                          handle,
                          data_len + 4,
                          data_len,
                          ATT_CID,
                          *data
                          )
        self.hci.write(cmd)


    def disconnect_connection(self, handle, reason):
        cmd = struct.pack(HCIPY_HCI_CMD_STRUCT_HEADER + "HB",
                          HCI_COMMAND_PKT,
                          DISCONNECT_CMD,
                          3,             # length
                          handle,
                          reason
                          )
        self.hci.write(cmd)

    def on_data(self, data):
        print("------------------------------------------")
        packet_indicator = data[0]
        print("packet_indicator = {}".format(packet_indicator))

        # 1 = Command Packets
        # 2 = Data Packets for ACL
        # 3 = Data Packets for SCO
        # 4 = Event Packets


        if HCI_EVENT_PKT == packet_indicator:
            evt = data[1]
            print("HCI_EVENT_PKT, evt={}".format(hex(evt)))

            # https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n2298
            # typedef struct {
            #    uint8_t		evt;
            #    uint8_t		plen;
            # } __attribute__ ((packed))	hci_event_hdr;
            # #define HCI_EVENT_HDR_SIZE	2


            if EVT_CMD_STATUS == evt:
                print("EVT_CMD_STATUS")

                # from: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n1860
                # typedef struct {
                #	uint8_t		status;
                #	uint8_t		ncmd;
                #	uint16_t	opcode;
                # } __attribute__ ((packed)) evt_cmd_status;

                s = struct.Struct('=B BB BBH')
                fields = s.unpack(data)
                evt_cmd_status = dict( packet_indicator  = fields[0],
                                       hdr_evt     = fields[1],
                                       hdr_plen    = fields[2],
                                       cmd_status  = fields[3],
                                       cmd_ncmd    = fields[4],
                                       cmd_opcode  = fields[5],
                                       )

                print("EVT_CMD_STATUS = {}".format(pformat(evt_cmd_status)))

            elif EVT_DISCONN_COMPLETE == evt:
                print("EVT_DISCONN_COMPLETE")
                # from: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n1780
                # #define EVT_DISCONN_COMPLETE		0x05
                # typedef struct {
                #     uint8_t		status;
                #     uint16_t	handle;
                #     uint8_t		reason;
                # } __attribute__ ((packed)) evt_disconn_complete;
                # #define EVT_DISCONN_COMPLETE_SIZE 4

                s = struct.Struct('=B BB   BHB')
                fields = s.unpack(data)
                evt_disconn_complete = dict(
                    status=fields[3],
                    handle=fields[4],
                    reason=fields[5],
                )

                print("evt_disconn_complete = {}".format(pformat(evt_disconn_complete)))
                exit(0)

            elif EVT_LE_META_EVENT == evt:
                print("EVT_LE_META_EVENT")

                # from: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n2146
                # #define EVT_LE_META_EVENT	0x3E
                # typedef struct {
                #     uint8_t		subevent;
                #     uint8_t		data[0];
                # } __attribute__ ((packed)) evt_le_meta_event;
                # #define EVT_LE_META_EVENT_SIZE 1

                subevent= data[3]

                #HCIPY_HCI_EVENT_PKT_STRUCT_HEADER =

                if EVT_LE_CONN_COMPLETE == subevent:
                    # from: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n2153
                    # #define EVT_LE_CONN_COMPLETE	0x01
                    # typedef struct {
                    #     uint8_t		status;
                    #     uint16_t	handle;
                    #     uint8_t		role;
                    #     uint8_t		peer_bdaddr_type;
                    #     bdaddr_t	peer_bdaddr;
                    #     uint16_t	interval;
                    #     uint16_t	latency;
                    #     uint16_t	supervision_timeout;
                    #     uint8_t		master_clock_accuracy;
                    # } __attribute__ ((packed)) evt_le_connection_complete;
                    # #define EVT_LE_CONN_COMPLETE_SIZE 18

                    s = struct.Struct('=B B BB B H B B 6B HHH B')
                    fields = s.unpack(data)
                    evt_le_connection_complete = dict(
                        status      = fields[4],
                        handle      = fields[5],
                        role        = fields[6],
                        peer_bdaddr_type = fields[7],
                        peer_bdaddr = fields[8:14],
                        interval    = fields[14] * 1.25,
                        latency     = fields[15],
                        supervision_timeout = fields[16] * 10,
                        master_clock_accuracy = fields[17],
                    )

                    print("evt_le_connection_complete = {}".format(pformat(evt_le_connection_complete)))

                elif EVT_LE_CONN_UPDATE_COMPLETE == subevent:
                    # from: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n2177
                    # #define EVT_LE_CONN_UPDATE_COMPLETE	0x03
                    # typedef struct {
                    #     uint8_t		status;
                    #     uint16_t	handle;
                    #     uint16_t	interval;
                    #     uint16_t	latency;
                    #     uint16_t	supervision_timeout;
                    # } __attribute__ ((packed)) evt_le_connection_update_complete;
                    # #define EVT_LE_CONN_UPDATE_COMPLETE_SIZE 9

                    s = struct.Struct('=B B BB  B 4H')
                    fields = s.unpack(data)
                    evt_le_connection_update_complete = dict(
                        status   = fields[4],
                        handle   = fields[5],
                        interval = fields[6] * 1.25,
                        latency  = fields[7],
                        supervision_timeout = fields[8] * 10,
                    )

                    print("evt_le_connection_update_complete = {}".format(pformat(evt_le_connection_update_complete)))

                    self.write_handle(evt_le_connection_update_complete['handle'], decode('020001', 'hex'))

        elif HCI_ACLDATA_PKT == packet_indicator:
            print("HCI_ACLDATA_PKT")
            # from: https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/lib/hci.h#n2304
            # typedef struct {
            #     uint16_t	handle;		/* Handle & Flags(PB, BC) */
            #     uint16_t	dlen;
            # } __attribute__ ((packed))	hci_acl_hdr;
            # #define HCI_ACL_HDR_SIZE	4

            # TODO: decode this in a cleaner way...
            if data[1] >> 12 == ACL_START and (data[8] << 8 + data[7]) == ATT_CID:
                # s = struct.Struct('=B ...')
                # fields = s.unpack(data)
                # evt_ = dict(
                #     _=fields[1],
                #
                # )

                handle = data[1] & 0x0fff
                payload = data[9:-1]

                print('ACL data');
                print('\t{}'.format(handle))
                print('\t{}'.format(payload))

                self.disconnect_connection(handle, HCI_OE_USER_ENDED_CONNECTION)


    def run(self):
        self.set_filter()
        self.hci.start()

        self.create_connection('B8:27:EB:12:E9:E4', LE_PUBLIC_ADDRESS)  # eenie
        #self.create_connection('ED:8A:7E:36:33:61', LE_RANDOM_ADDRESS)  # BBC micro:bit [vovot]
        #self.create_connection('f4:58:8e:30:7b:43', LE_RANDOM_ADDRESS)  # Puck.js


if __name__ == "__main__":
    ble_scan_test = BluetoothLEConnectionTest()
    ble_scan_test.run()

    pause()
