#!/usr/bin/env python3
"""
iogp.data.asn1: Parsers for ASN.1 / DER / Windows catalog (.cat) files.

Reference:
    - Certificate ASN.1 grammar:
        - <https://docs.microsoft.com/en-us/windows/win32/seccertenroll/about-x-509-public-key-certificates>

Author: Vlad Topan (vtopan/gmail)
"""
from .oid import OID, OID_MAP

import base64
import re
import sys
import time
import types


ASN1_TAG_BOOLEAN = 0x01
ASN1_TAG_INTEGER = 0x02
ASN1_TAG_BIT_STRING = 0x03
ASN1_TAG_OCTET_STRING = 0x04
ASN1_TAG_NULL = 0x05
ASN1_TAG_OBJECT_IDENTIFIER = 0x06
ASN1_TAG_ENUMERATED = 0x0A
ASN1_TAG_UTF8String = 0x0C
ASN1_TAG_PrintableString = 0x13
ASN1_TAG_TeletexString = 0x14
ASN1_TAG_IA5String = 0x16
ASN1_TAG_UTCTime = 0x17
ASN1_TAG_GeneralizedTime = 0x18
ASN1_TAG_VisibleString = 0x1A
ASN1_TAG_BMPString = 0x1E
ASN1_TAG_SEQUENCE = 0x30
ASN1_TAG_SET = 0x31

ASN1_TAG_NAMES = {v: k[9:] for k, v in globals().items() if k.startswith('ASN1_TAG_')}
ASN1_TAG_VALUES = {v: k for k, v in ASN1_TAG_NAMES.items()}

CRYPT_SUBJ_TYPES = {
    'DE351A42-8E59-11D0-8C47-00C04FC295EE': 'CRYPT_SUBJTYPE_FLAT_IMAGE',
    'C689AABA-8E78-11d0-8C47-00C04FC295EE': 'CRYPT_SUBJTYPE_CABINET_IMAGE',
    'C689AAB8-8E78-11D0-8C47-00C04FC295EE': 'CRYPT_SUBJTYPE_PE_IMAGE',
    'DE351A43-8E59-11D0-8C47-00C04FC295EE': 'CRYPT_SUBJTYPE_CATALOG_IMAGE',
    '9BA61D3F-E73A-11D0-8CD2-00C04FC295EE': 'CRYPT_SUBJTYPE_CTL_IMAGE',
    'C689AAB9-8E78-11D0-8C47-00C04FC295EE': 'CRYPT_SUBJTYPE_JAVACLASS_IMAGE',
    '941C2937-1292-11D1-85BE-00C04FC295EE': 'CRYPT_SUBJTYPE_SS_IMAGE',
    }

KEY_USAGE = [
    'DigitalSignature',
    'NonRepudiation',
    'KeyEncipherment',
    'DataEncipherment',
    'KeyAgreement',
    'KeyCertSign',
    'CRLSign',
    'EncipherOnly',
    'DecipherOnly',
    ]

RX = {
    'utf16le': (rb'^([^\0]\0)+\0\0$',),
    'ascii': (rb'^[\r\n\t\x20-\x7E]+$',),
    }
for k in RX:
    RX[k] = re.compile(*RX[k])



class ASN1Entry:
    """
    ASN.1 entry (has a tag, a value, an offset and a size).
    """

    def __init__(self, data=None, offset=0, decode=True, heuristic=False):
        self.is_decoded = self.is_container = self.is_oid = False
        self.oid_name = None

        if data is not None:
            self.parse(data=data, offset=offset, decode=decode, heuristic=heuristic)

    def parse(self, data=None, offset=None, decode=True, heuristic=False):
        """
        Parse an ASN.1 entry.
        """
        self._data = data
        self.offset = offset
        self._raw_data = None
        b = data[offset + 1]
        multibyte, size, voffset = bool(b & 0x80), b & 0x7F, offset + 2
        if multibyte:
            if size == 0:
                # indefinite form - look for 00 00
                raise NotImplementedError('todo')
            voffset, size = voffset + size, int.from_bytes(data[voffset:voffset + size], byteorder='big')
        # self.raw_data = data[voffset:voffset + size]
        self.tag = data[offset]
        self.data_offset = voffset
        self.data_size = size
        self.size = voffset + size - offset
        self.tag_name = ASN1_TAG_NAMES.get(self.tag)
        if decode:
            self.decode(heuristic=heuristic)

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self._data[self.offset:self.offset + self.size]
        return self._raw_data

    def decode(self, heuristic=False):
        """
        Decode a parsed ASN.1 entry.
        """
        tag, offset, size = self.tag, self.data_offset, self.data_size
        raw_data = self.value_raw_data = self._data[offset:offset + size]
        tag_class, tag_value = tag >> 5, tag & 0x1F
        if tag in (ASN1_TAG_SET, ASN1_TAG_SEQUENCE):
            value = ASN1Entry.parse_container(self._data, offset, end=offset + size, decode=True,
                    heuristic=heuristic)
            self.is_container = True
        elif tag == ASN1_TAG_BOOLEAN:
            value = int(bool(self._data[offset]))   # can't subclass bool() to add the .offset attribute
        elif tag in (ASN1_TAG_BIT_STRING, ASN1_TAG_OCTET_STRING):
            value = raw_data
            if tag == ASN1_TAG_BIT_STRING:
                self.ignore_bits = value[0]
                value = value[1:]
            if heuristic and value[0] == 0x30:
                try:
                    value = ASN1Entry.parse_container(self._data,
                            offset + int(tag == ASN1_TAG_BIT_STRING),
                            end=offset + size, decode=True, heuristic=heuristic)
                    self.tag_name = 'Container'
                    self.is_container = True
                except ValueError:
                    pass
        elif tag in (ASN1_TAG_UTCTime, ASN1_TAG_GeneralizedTime):
            value = raw_data.decode('ascii')
        elif tag in (ASN1_TAG_PrintableString, ASN1_TAG_IA5String, ASN1_TAG_TeletexString,
                ASN1_TAG_VisibleString):
            value = raw_data.decode('ascii')
        elif tag == ASN1_TAG_BMPString:
            value = raw_data.decode('UTF-16-BE')
        elif tag == ASN1_TAG_UTF8String:
            value = raw_data.decode('utf8')
        elif tag == ASN1_TAG_NULL:
            value = None
        elif tag == ASN1_TAG_OBJECT_IDENTIFIER:
            value = OID.extract(self._data, offset, size)
            self.is_oid = True
            self.oid_name = OID_MAP.get(value, None)
        elif tag in (ASN1_TAG_INTEGER, ASN1_TAG_ENUMERATED):
            value = int.from_bytes(raw_data, byteorder='big')
        elif tag_class == 0x04: # context-defined
            self.tag_name = 'ContextDefined'
            value = raw_data if size else None
        elif tag_class == 0x05: # context-defined | constructed
            self.tag_name = 'Container'
            value = ASN1Entry.parse_container(self._data, offset, end=offset + size, decode=True,
                    heuristic=heuristic)
            self.is_container = True
        else:
            raise ValueError(f'Unknown type tag: 0x{tag:x} ({tag})!')
        self.is_decoded = True
        if type(value) in (int, str, bytes):
            value = wrap_with_offset_size(value, self.data_offset, self.data_size)
        self.value = value

    @classmethod
    def parse_container(cls, data, offset=0, end=None, max_count=None, decode=True, heuristic=False):
        """
        Parse any number of ASN.1-encoded entries and return a list of raw results.

        :return: List of ASN1Entry().
        """
        result = []
        if end is None:
            end = len(data)
        count = 0
        base_offset = offset
        while offset + 1 < end and ((not max_count) or count < max_count):
            entry = cls(data, offset, decode=decode, heuristic=heuristic)
            result.append(entry)
            offset = entry.data_offset + entry.data_size
            count += 1
        if (not max_count) and offset != end:
            raise ValueError(f'Invalid ASN.1 stream end (last offset: {offset}, data ends at {end})!')
        result = wrap_with_offset_size(result, base_offset, offset - base_offset)
        return result

    def dump(self, title=None, indent=0):
        """
        Dump ASN.1 object.
        """
        res = []
        if title:
            res.append(title)
        value = self.value
        if not self.is_container:
            res.append(f"{indent * '  '}{ASN1_TAG_NAMES.get(self.tag, hex(self.tag))}: {self.str_value}")
        else:
            res.append(f"{indent * '  '}#<{indent}> [{len(value)}]")
            for e in value:
                res.append(e.dump(indent=indent + 1))
        return '\n'.join(res)

    @property
    def str_value(self):
        """
        Render this entry's value a (flattened) string.
        """
        if self.is_container:
            res = '[%s]' % ';'.join(x.str_value for x in self.value)
        elif not isinstance(self.value, bytes):
            res = str(self.oid_name or self.value)
        elif RX['ascii'].search(self.value):
            res = self.value.decode('ascii')
        else:
            res = bytes.hex(self.value)
        res = wrap_with_offset_size(res, self.data_offset, self.data_size)
        return res

    def __getitem__(self, key):
        return self.value[key]

    def __len__(self):
        if self.is_container:
            return len(self.value)
        raise ValueError(f'{self} has no len() (is not a container)!')

    def __repr__(self):
        return f'ASN1Entry<0x{self.tag:02X}:{self.value.__class__.__name__}@{self.offset}[{self.size}]>'

    def is_certificate(self):
        """
        Check if this entry is a certificate.
        """
        return self.is_container and len(self) == 3 and len(self[0]) in (7, 8)

    def identify(self):
        """
        Identify the ASN.1.
        """
        # todo
        '''
        try:
            if len(self) == 3 and len(self[0]) == 6 and self[0][1][0].value == '1.2.840.113549.1.1.5' \
                    and :
                return
        except IndexError:
            return None
        '''



def parse_oid_map(root):
    """
    Parse a list of OID-value entries.
    """
    res = {}
    for e in root.value:
        res[e[0][0].oid_name] = e[0][1].value
    wrap_with_offset_size(res, root.data_offset, root.data_size)
    return res


def wrap_with_offset_size(obj, offset, size):
    obj = types.new_class('ex_' + obj.__class__.__name__, (type(obj),))(obj)
    obj.offset = offset
    obj.size = size
    return obj


def parse_certificate(filename_or_root, offset=0):
    """
    Parse a certificate.

    :param filename_or_root: Filename (str), data (bytes) or ASN1Entry() instance.
    """
    res = wrap_with_offset_size({}, offset, None)
    try:
        if isinstance(filename_or_root, str):
            data = open(filename_or_root, 'rb').read()
        if isinstance(data, bytes):
            root = ASN1Entry(data)
        else:
            root = filename_or_root
        assert len(root) == 3
        info = root[0]
        if len(info) == 7:
            ver = 1
            assert info[0].value == 1
        elif len(info) == 8:
            ver = 2
            assert info[0][0].value == 2
        else:
            raise ValueError(f'Invalid field count: {len(info)}!')
        cert = res['Certificate'] = wrap_with_offset_size({}, info.data_offset, info.data_size)
        cert['Version'] = ver
        assert ver in (1, 2)
        if ver == 1:
            cert['Issued to'] = parse_oid_map(info[1][0][0][0])
            cert['Issued to / hash type'] = info[1][1][1][0].oid_name
            cert['Issued to / hash'] = info[1][1][2].str_value
            cert['Issued by'] = parse_oid_map(info[2][0][0][0])
            cert['Valid from'] = format_asn1_time(info[5][0])
            cert['Valid to'] = format_asn1_time(info[5][1])
        elif ver == 2:
            cert['Serial number'] = hex(info[1].value)[2:]
            cert['Issued by'] = parse_oid_map(info[3])
            cert['Issued to'] = parse_oid_map(info[5])
            cert['Valid from'] = format_asn1_time(info[4][0])
            cert['Valid to'] = format_asn1_time(info[4][1])
            cert['Algorithm'] = info[6][0][0].oid_name
            pkey = ASN1Entry(info[6][1].value)
            pk_offs = info[6][1].data_offset
            pkey[0].data_offset += pk_offs
            pkey[1].data_offset += pk_offs
            cert['Public Key'] = {'Modulus':wrap_with_offset_size(hex(pkey[0].value)[2:],
                    pkey[0].data_offset, pkey[0].data_size), 'Exponent': pkey[1].value}
            cert['Key size'] = int((pkey[0].data_size - 1) * 8)
            cert['Extensions'] = extensions = wrap_with_offset_size({}, info[7][0].data_offset, info[7][0].data_size)
            for e in info[7][0].value:
                if e[0].oid_name == 'Key Usage':
                    entry = ASN1Entry(e[1].value)
                    value = int.from_bytes(entry.value, 'big') >> entry.ignore_bits
                    value = ','.join(KEY_USAGE[i] for i in range(len(KEY_USAGE)) if value & (1 << i))
                    value = wrap_with_offset_size(value, entry.data_offset, entry.data_size)
                elif isinstance(e[1].value, bytes):
                    field = ASN1Entry(e[1].value)
                    if field.is_container:
                        # todo: properly parse the very homogenous ASN.1-encoded additional fields
                        value = field.str_value
                    elif isinstance(field.value, bytes):
                        value = wrap_with_offset_size(bytes.hex(field.value), field.data_offset, field.data_size)
                    else:
                        value = field.value
                else:
                    value = e[1].value
                value.offset += e[1].offset
                extensions[e[0].oid_name] = value
        res['Hash type'] = wrap_with_offset_size(root[1][0].oid_name, root[1][0].data_offset, root[1][0].data_size)
        res['Signature'] = bytes.hex(root[2].value)
    except (IndexError, ValueError, KeyError, AssertionError) as e:
        raise ValueError from e
    return res


def format_asn1_time(entry):
    """
    Parse and format ASN.1 time value.
    """
    value = entry.value
    tvalue = time.strptime(value, f"%{'y' if len(value) == 13 else 'Y'}%m%d%H%M%SZ")
    res = time.strftime("%d.%m.%Y, %H:%M:%S UTC", tvalue) + f' ({value})'
    wrap_with_offset_size(res, entry.data_offset, entry.data_size)
    return res


def parse_catalog(filename_or_root, embedded=None):
    """
    Parse a Windows catalog (.cat) file.

    :param filename_or_root: Filename (str) or ASN1Entry() instance.
    """
    res = {}
    try:
        if isinstance(filename_or_root, str):
            data = open(filename_or_root, 'rb').read()
            root = ASN1Entry(data)
        else:
            root = filename_or_root
        # root.dump()
        # print(root[0])
        assert root.is_container and len(root.value) == 2 and root[0].oid_name == 'signedData'
        certinfo = root[1][0].value
        assert len(certinfo) == 5
        res['Catalog info'] = crtres = {}
        crtres['Version'] = certinfo[0].value
        crtres['Algorithm'] = certinfo[1][0][0].oid_name
        assert not certinfo[1][0][1].value
        assert len(certinfo[2][1]) == 1 and certinfo[2][0].value == '1.3.6.1.4.1.311.10.1' # CTL
        ctl = certinfo[2][1][0].value
        assert len(ctl) in (5, 6) and ctl[0][0].oid_name == 'CATALOG_LIST'
        crtres['Subject usage'] = repr(ctl[0][0].value)
        crtres['List identifier'] = bytes.hex(ctl[1].value)
        crtres['Effective time'] = f'{format_asn1_time(ctl[2])} ({ctl[2].value})'
        assert ctl[3][0].oid_name in ('CATALOG_LIST_MEMBER', 'CATALOG_LIST_MEMBER_V2')
        entries = ctl[4]
        res['Entries'] = crtres = []
        for e in entries:
            crtentry = {}
            crtres.append(crtentry)
            attrs = e[1]
            if RX['utf16le'].search(e[0].value):
                tag = e[0].value.decode('utf16')
            else:
                tag = bytes.hex(e[0].value)
            crtentry['Tag'] = tag.lower()
            for attr in attrs:
                if attr[0].oid_name == 'CAT_MEMBERINFO2_OBJID':
                    assert attr[1][0].value is None
                elif attr[0].oid_name == 'SPC_INDIRECT_DATA_OBJID':
                    if attr[1][0][0][0].oid_name == 'SPC_GLUE_RDN_OBJID':
                        if attr[1][0][0][1][0].value:
                            val = attr[1][0][0][1][0].value
                            try:
                                val = val.decode('UTF-16-BE')
                            except UnicodeError:
                                pass
                            if val != '<<<Obsolete>>>':
                                raise ValueError(f'Unknown SPC_GLUE_RDN_OBJID value: {val}!')
                            crtentry['GLUE-RDN-tag'] = val
                        hashinfo = attr[1][0][1]
                        crtentry['Hash type'] = hashinfo[0][0].oid_name
                        crtentry['Hash'] = bytes.hex(hashinfo[1].value)
                    elif attr[1][0][0][0].oid_name == 'SPC_PE_IMAGE_DATA_OBJID':
                        crtentry['Filetype'] = 'SPC_PE_IMAGE_DATA_OBJID'
                    else:
                        raise ValueError(f'Unknown field type: {attr[1][0][0][0].value}')
                elif attr[0].oid_name == 'CAT_MEMBERINFO_OBJID':
                    clsid = attr[1][0][0].value.strip('{}')
                    subjtype = CRYPT_SUBJ_TYPES[clsid]
                    crtentry['Subject Type'] = subjtype
                    crtentry['Subject CLSID'] = clsid
                elif attr[0].oid_name == 'CAT_NAMEVALUE_OBJID':
                    name, flags, val= attr[1][0].value
                    val = val.value
                    if isinstance(val, bytes):
                        try:
                            val = val.decode('utf16').rstrip('\0')
                        except UnicodeError:
                            pass
                    crtentry[name.value] = f'{val} ({hex(flags.value)})'
                else:
                    raise ValueError(f'Unknown attribute type: {attr[0].oid_name}')
        if len(ctl) > 5:
            assert len(ctl[5]) == 1
            if len(ctl[5][0]):
                res['Name-value entries'] = crtres = {}
            for namevalue in ctl[5][0]:
                assert namevalue[0].oid_name == 'CAT_NAMEVALUE_OBJID'
                nvdata = ASN1Entry.parse_container(namevalue[1].value)
                for e in nvdata:
                    name, flags, v = e.value
                    val = v.value
                    try:
                        val = val.decode('utf16').rstrip('\0')
                    except UnicodeError:
                        pass
                    crtres[name.value] = f'{val} ({hex(flags.value)})'
        res['Certificates'] = crtres = []
        for cert in certinfo[3]:
            crtres.append(parse_certificate(cert))
            if embedded is not None:
                embedded.append(cert.raw_data)
        res['Timestamping'] = crtres = {}
        ts = certinfo[4][0]
        crtres['Hash type'] = ts[2][0].oid_name
        crtres['Algorithm'] = ts[4][0].oid_name
        crtres['Public key'] = bytes.hex(ts[5].value)
        try:
            certs = ts[6][0][1][0][1][0][3].value
            # todo: extract more info about the countersignature
            crtres['Certificates'] = crtlst = []
            for cert in certs:
                if len(cert) == 3:
                    if embedded is not None:
                        embedded.append(cert.raw_data)
                    crtlst.append(parse_certificate(cert))
        except (ValueError, AssertionError, IndexError):
            pass    # todo: fixme - timestamping data needs better parsing
            sys.stderr.write('WARNING: Timestamping countersignature information is incomplete!\n')
    except (IndexError, ValueError, KeyError, AssertionError) as e:
        raise ValueError from e
    return res


def parse_certificate_file(filename):
    """
    Parse .cer or .p7b certificate file.
    """
    data = open(filename, 'rb').read()
    if data.startswith(b'-----BEGIN '):
        data = data.split(b'-----')[2]
        data = base64.b64decode(data)
    return parse_certificate(ASN1Entry(data))
