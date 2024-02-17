"""
DataView: wrapper over raw binary data, files etc.

Each DataView instance has a unique (numeric) `.id`; if the DataView.open() factory is used,
identical buffers will point to the same DataView when multiple instances are created. The same
filename (case sensitive) will always have the same DataView instance associated with it.

Author: Vlad Topan (vtopan/gmail)
"""
import collections
import hashlib
import mmap
import os
import struct
import threading

from .ds import AttrDict
from .fileid import get_file_type


PREFILTER_SIZE = 2048
MAX_CMP_HASH_SIZE = 64 * 1024 * 1024
BUFFER_ID_LOCK = threading.Lock()


class DataView:
    """
    Data view object: wrapper over raw binary data, files etc.

    :param data: The raw data (bytes or bytearray) or filename.
    :param filename: The file name containing the data.
    :param parent: DataView() instance.
    :param relation: `str`, relation with the parent (if any).
    :param virtual: False if the filename exists (can be overriden).
    """
    MAP = {}                                    # maps `.id`s to DataView() instances
    FILENAME_MAP = {}                           # maps filenames to DataView() instances
    PREFLT_MAP = collections.defaultdict(list)  # maps prefilter-MD5s (on the first part of buffers)
                                                # to lists of DataView() instances


    def __init__(self, data=None, filename=None, name=None, readonly=True, parent=None,
                relation=None, virtual=None):
        if data is None and filename is None:
            data = b''
        self.name = name
        self._full_hash = None
        if type(data) is str:
            filename, data = data, None
        if data is not None and not readonly and type(data) is bytes:
            data = bytearray(data)
        BUFFER_ID_LOCK.acquire()
        self.id = len(DataView.MAP)
        DataView.MAP[self.id] = self
        BUFFER_ID_LOCK.release()
        self.fullname = os.path.abspath(filename) if filename else None
        if virtual is None:
            virtual = not (filename and os.path.isfile(self.fullname))
        if filename and not virtual:
            self.FILENAME_MAP[self.fullname] = self
        self.rawdata = data
        self.filename = filename
        self.readonly = readonly
        self._data = None
        self.mm = self.fh = None
        self.parent = parent
        self.virtual = virtual
        self.relation = relation
        if parent:
            self.parent.children.append(self)
        self.children = []
        self.hashes = None
        self.pf_hash = prefilter_hash(self)
        DataView.PREFLT_MAP[self.pf_hash].append(self)

    @classmethod
    def open(cls, data=None, filename=None, id=None, **kwargs):
        """
        Creates a new DataView or returns an existing one based on the given `data`,
        `filename` or `id`.
        """
        if id:
            return DataView.MAP[id]
        if filename and (not kwargs.get('virtual')) and os.path.abspath(filename) in DataView.MAP:
            return DataView.FILENAME_MAP[os.path.abspath(filename)]
        rdata = data if data else open(filename, 'rb').read(PREFILTER_SIZE)
        pf_hash = prefilter_hash(rdata)
        f_hash = None
        if pf_hash in DataView.PREFLT_MAP:
            for e in DataView.PREFLT_MAP[pf_hash]:
                if f_hash is None:
                    f_hash = full_hash(data) if data else full_hash_from_file(filename)
                if f_hash == e.full_hash:
                    return e
        # new buffer, create DataView() instance
        return DataView(data=data, filename=filename, **kwargs)

    @property
    def full_hash(self):
        """
        "Full" (up to MAX_CMP_HASH_SIZE) file hash.
        """
        if not self._full_hash:
            self._full_hash = full_hash(self.raw)
        return self._full_hash

    @property
    def raw(self):
        """
        This is the actual data. The file view is created automagically as needed and can be closed
        with .close().
        """
        if self._data is not None:
            return self._data
        if self.rawdata is not None:
            self._data = self.rawdata
        else:
            if self.virtual:
                raise ValueError('Attempted to open a virtual filename!')
            mode, access = 'rb', mmap.ACCESS_READ
            if not self.readonly:
                mode = 'rb+'
                access |= mmap.ACCESS_WRITE
            self.fh = open(self.filename, mode)
            self.mm = mmap.mmap(self.fh.fileno(), 0, access=access)
            self._data = self.mm
        return self._data

    def startswith(self, data):
        return self.raw[:len(data)] == data

    @property
    def file_type(self):
        if not hasattr(self, '_file_type'):
            self._file_type = get_file_type(self.raw)
        return self._file_type

    def close(self):
        """
        Close the file (if open).
        """
        if self._data is not None:
            if self.mm:
                self.mm.close()
            if self.fh:
                self.fh.close()
            self.mm = self.fh = None
            self._data = None

    def find(self, pattern, offset=0):
        """
        Find a bytes pattern in the data.
        """
        return self.raw.find(pattern, offset)

    def __setitem__(self, item, value):
        if self.readonly:
            raise ValueError('Readonly flag set!')
        self.raw[item] = value

    def __getitem__(self, item):
        return self.raw[item]

    def __len__(self):
        return len(self.raw)

    def read_I2(self, offset):
        """
        Read a two-byte unsigned int from offset.
        """
        return struct.unpack('<H', self.raw[offset:offset + 2])[0]

    def read_I4(self, offset):
        """
        Read a four-byte unsigned int from offset.
        """
        return struct.unpack('<I', self.raw[offset:offset + 4])[0]

    def read_I8(self, offset):
        """
        Read an eight-byte unsigned int from offset.
        """
        return struct.unpack('<Q', self.raw[offset:offset + 8])[0]

    def read_SI4(self, offset):
        """
        Read a four-byte signed int from offset.
        """
        return struct.unpack('<i', self.raw[offset:offset + 4])[0]

    def save(self):
        """
        Save changes (only relevant if both data and filename were passed to the constructor).
        """
        if self.filename and self.rawdata:
            open(self.filename, 'wb').write(self.rawdata)

    def _calculate_hashes(self):
        hashes = {k: getattr(hashlib, k)() for k in ('md5', 'sha1', 'sha256')}
        chunk_size = 64 * 4096
        for i in range(0, len(self), chunk_size):
            chunk = self[i:i + chunk_size]
            for h in hashes.values():
                h.update(chunk)
        self.hashes = AttrDict({k: v.hexdigest() for k, v in hashes.items()})

    @property
    def md5(self):
        """
        The buffer's MD5 hash.
        """
        if not self.hashes:
            self._calculate_hashes()
        return self.hashes.md5

    @property
    def sha1(self):
        """
        The buffer's SHA-1 hash.
        """
        if not self.hashes:
            self._calculate_hashes()
        return self.hashes.sha1

    @property
    def sha256(self):
        """
        The buffer's SHA-256 hash.
        """
        if not self.hashes:
            self._calculate_hashes()
        return self.hashes.sha256



def prefilter_hash(data):
    """
    Computes the prefilter hash for buffer comparison by contents.
    """
    return hashlib.md5(data[:PREFILTER_SIZE]).hexdigest()


def full_hash(data, tail=None):
    """
    Computes the full hash for buffer comparison by contents.
    """
    h = hashlib.sha256(data[:MAX_CMP_HASH_SIZE])
    if len(data) > MAX_CMP_HASH_SIZE and not tail:
        tail = data[-PREFILTER_SIZE:]
    if tail:
        h.update(tail)
    return h.hexdigest()


def full_hash_from_file(filename):
    """
    Computes the full file-comparison hash for a filename.
    """
    with open(filename, 'rb') as f:
        if os.path.getsize(filename) > MAX_CMP_HASH_SIZE:
            data = f.read(MAX_CMP_HASH_SIZE)
            f.seek(-PREFILTER_SIZE, 2)
            tail = f.read()
        else:
            data, tail = f.read(), None
        return full_hash(data, tail)
