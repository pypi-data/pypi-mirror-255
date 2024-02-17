#!/usr/bin/env python3
"""
iogp.net.packet: Network packet and .pcap processing library.

Author: Vlad Topan (vtopan/gmail)
"""

import binascii
import struct


BASE_TCPDUMP    = 1000
BASE_ETHER      = 2000
BASE_IP         = 3000

# TCPDump LL IDs (1000 + IDs from http://www.tcpdump.org/linktypes.html)
Ethernet        = BASE_TCPDUMP + 1
IP              = BASE_TCPDUMP + 101

# EtherType-based (2000 + EtherType)
IPv4            = BASE_ETHER + 0x0800
IPv6            = BASE_ETHER + 0x86DD
ARP             = BASE_ETHER + 0x0806
CDP             = BASE_ETHER + 0x2000
LLDP            = BASE_ETHER + 0x88CC
IEEE8021Q       = BASE_ETHER + 0x8100

# IP protocols (3000 + IP protocol number)
ICMP            = BASE_IP + 1
IGMP            = BASE_IP + 2
IPv4Inv4        = BASE_IP + 4
TCP             = BASE_IP + 6
UDP             = BASE_IP + 17
IPv6Inv4        = BASE_IP + 41


# Protocol info: (name, layer);
PROTOCOLS = {
    Ethernet:('Ethernet', 1),
    ARP:('ARP', 2),
    CDP:('CDP', 2),
    LLDP:('LLDP', 2),
    IP:('IP', 3),                   # named "RAW", which means IPv4/6
    IPv4:('IPv4', 3),
    IPv6:('IPv6', 3),
    ICMP:('ICMP', 3),
    IGMP:('IGMP', 3),
    UDP:('UDP', 4),
    TCP:('TCP', 4),
    }



class PCap:
    """
    Wraps a packet capture file.

    @param source: The data source (a filename or raw binary data).
    """

    def __init__(self, source=None):
        self.packets = []
        self.data = b''
        if source:
            self.parse(source)


    def parse(self, source):
        """
        Parses a packet capture file.

        :param source: The data source (a filename or raw binary data).
        """
        if type(source) == str:
            data = open(source, 'rb').read()
            self.filename = source
        else:
            data = source
            self.filename = '<rawdata>'
        self.bom = bom = '>' if data[:4] == b'\xA1\xB2\xC3\xD4' else '<'
        hdr = struct.unpack(bom + 'HHlLLL', data[4:24])
        self.ver = (hdr[0], hdr[1])
        self.max_len = hdr[4]
        self.layer = hdr[5]     # link-layer header type
        pos = 24
        num = 1
        while pos < len(data):
            ts_sec, ts_us, size, orig_size = struct.unpack(bom + 'LLLL', data[pos:pos + 16])
            pos += 16
            pdata = data[pos:pos + size]
            pos += size
            if size < orig_size:
                pdata += b'\0' * (orig_size - size)
            packet = Packet(pdata, ts=ts_sec, ts_us=ts_us, proto=BASE_TCPDUMP + self.layer, num=num)
            self.packets.append(packet)
            num += 1
        return self.packets


    def __str__(self):
        return "PCap[%s]:[%d.%d/%s/%d/%d]" % ((self.filename,) + self.ver + (self.bom, self.max_len, self.layer))



class Packet:
    """
    Basic network packet parser.

    :param data: The data buffer (may be longer than a packet).
    :param layer: The layer/protocol of the packet (see PROTOCOLS); default: 1 = Ethernet.
    :param num: Packet number inside PCAP (1-based).
    :param ts: Timestamp (UTC), as int.
    :param ts_us: Timestamp microseconds as int.
    """

    def __init__(self, data, proto=Ethernet, parent=None, num=0, ts=None, ts_us=None):
        self.ts = ts
        self.ts_us = ts_us
        self.num = num
        self.proto = proto
        self.layers = {}
        self.fields = {}
        self.parent = parent
        self.next = self.next_type = None
        self.data = data
        self.hsize = len(data)
        if self.proto in _FIELDS:
            for finfo in _FIELDS[self.proto]:
                fname, fval, pos = finfo[:3]
                if pos == 'raw':
                    pass
                elif pos == 'self':
                    fval = fval(self)
                else:
                    pos = finfo[2]
                    if type(fval) == str:
                        pat = fval
                        nibble = None
                        if fval[0] == 'n':
                            # nibble
                            pat = 'B'
                            nibble = fval[1]
                        fval = struct.unpack('>' + pat, data[pos:pos + struct.calcsize(pat)])[0]
                        if nibble:
                            fval = (fval >> 4) if nibble == 'h' else (fval & 0xF)
                    else:
                        fval = fval(data[pos:pos + finfo[3]])
                setattr(self, fname, fval)
                self.fields[fname] = fval
        if self.proto == Ethernet:
            # Ethernet
            if self.type == IEEE8021Q:
                self.vlan, self.type = struct.unpack('>HH', data[14:18])
                self.hsize += 4
            self.next_type = BASE_ETHER + self.type
        elif self.proto in [IPv4, IPv6]:
            self.next_type = self.protocol + BASE_IP
        if self.next_type:
            self.payload = data[self.hsize:]
            self.next = Packet(self.payload, proto=self.next_type, parent=self)
            self.payload = self.payload[:len(self.next)]
            self.data = data[:self.hsize + len(self.payload)]


    def __len__(self):
        return getattr(self, 'size', len(self.data) if self.data else 0)


    def __str__(self):
        _str = getattr(self, '_str', ' '.join('%02X' % c for c in self.data[:16]) + '...') % self.__dict__
        s = '%s[%d] %s' % (PROTOCOLS.get(self.proto, ('?/%d' % self.proto,))[0], len(self), _str)
        s += '\nRAW:' + encode_hex(self.data[:self.hsize])[:64]
        if self.next:
            s += '\n' + '\n'.join(['  ' + x for x in str(self.next).split('\n')])
        elif len(self) != self.hsize:
            s += '\n' + 'PAYLOAD: ' + encode_hex(self.data[self.hsize:])[:64]
        return s



def decode_mac(x):
    """
    Decode a MAC address from a binary (bytes) string.
    """
    return ':'.join('%02X' % e for e in x)


def decode_ip(x):
    """
    Decode an IP address (v4 or v6) from a binary (bytes) string.
    """
    if type(x) != bytes:
        x = list(ord(e) for e in x)
    if len(x) == 4:
        # ipv4
        return '.'.join(str(e) for e in x)
    else:
        # ipv6
        return ':'.join('%02X' % e for e in x)


def encode_hex(x):
    """
    Encode a binary string as hex.
    """
    return binascii.hexlify(x).upper().decode('utf8')


def unpack_be_gen(itype):
    def _unpack(data):
        return struct.unpack('>%s' % itype, data[:struct.calcsize(itype)])[0]
    _unpack.__name__ = 'unpack_be_%s' % itype
    return _unpack


# need the decoding functions to be declared for this
_FIELDS = {
    Ethernet: [
        ('vlan', None, 'raw'),
        ('dst', decode_mac, 0, 6),
        ('src', decode_mac, 6, 6),
        ('type', 'H', 12),
        ('hsize', 14, 'raw'),
        ('_str', '%(src)s->%(dst)s', 'raw'),
        ],
    IPv4: [
        ('ver', 'nh', 0),
        ('ihl', 'nl', 0),
        ('size', 'H', 2),
        ('hsize', lambda x:x.ihl * 4, 'self'),
        ('protocol', 'B', 9),
        ('src', decode_ip, 12, 4),
        ('dst', decode_ip, 16, 4),
        ('_str', '%(src)s->%(dst)s', 'raw'),
        ],
    TCP: [
        ('src', 'H', 0),
        ('dst', 'H', 2),
        ('seqnum', 'I', 4),
        ('acknum', 'I', 8),
        ('dataoffs', 'B', 12),
        ('flags', 'B', 13),
        ('winsize', 'H', 14),
        ('checksum', 'H', 16),
        ('urgent', 'H', 18),
        ('hsize', lambda x:x.dataoffs >> 2, 'self'),
        ('_str', '%(src)s->%(dst)s', 'raw'),
        ],
    UDP: [
        ('src', 'H', 0),
        ('dst', 'H', 2),
        ('size', 'H', 4),
        ('checksum', 'H', 6),
        ('hsize', 8, 'raw'),
        ('_str', '%(src)s->%(dst)s', 'raw'),
        ],
    }



if __name__ == '__main__':
    import math
    import sys
    import time
    for i, p in enumerate(PCap(sys.argv[1]).packets):
        print(f'#{p.num} @ {time.strftime("%Y.%m.%d,%H:%M:%S", time.gmtime(p.ts))}.{p.ts_us // 1000:03d}:', p)
