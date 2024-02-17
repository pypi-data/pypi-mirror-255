"""
iogp.data.archive: Archive processing APIs.

On Windows, archiveint.dll (libarchive 3.3.2?) is used (ships with Windows 10).
Code from libarchive's archive.h is used, license in external/libarchive.license.

Author: Vlad Topan (vtopan/gmail)
"""
import os
import ctypes
from ctypes import c_void_p, Structure, c_int, c_char_p, POINTER, byref
if os.name == 'nt':
    from ctypes import WINFUNCTYPE, windll


ARCHIVE_FORMAT_BASE_MASK = 0xff0000
ARCHIVE_FORMAT_CPIO = 0x10000
ARCHIVE_FORMAT_CPIO_POSIX = (ARCHIVE_FORMAT_CPIO | 1)
ARCHIVE_FORMAT_CPIO_BIN_LE = (ARCHIVE_FORMAT_CPIO | 2)
ARCHIVE_FORMAT_CPIO_BIN_BE = (ARCHIVE_FORMAT_CPIO | 3)
ARCHIVE_FORMAT_CPIO_SVR4_NOCRC = (ARCHIVE_FORMAT_CPIO | 4)
ARCHIVE_FORMAT_CPIO_SVR4_CRC = (ARCHIVE_FORMAT_CPIO | 5)
ARCHIVE_FORMAT_CPIO_AFIO_LARGE = (ARCHIVE_FORMAT_CPIO | 6)
ARCHIVE_FORMAT_SHAR = 0x20000
ARCHIVE_FORMAT_SHAR_BASE = (ARCHIVE_FORMAT_SHAR | 1)
ARCHIVE_FORMAT_SHAR_DUMP = (ARCHIVE_FORMAT_SHAR | 2)
ARCHIVE_FORMAT_TAR = 0x30000
ARCHIVE_FORMAT_TAR_USTAR = (ARCHIVE_FORMAT_TAR | 1)
ARCHIVE_FORMAT_TAR_PAX_INTERCHANGE = (ARCHIVE_FORMAT_TAR | 2)
ARCHIVE_FORMAT_TAR_PAX_RESTRICTED = (ARCHIVE_FORMAT_TAR | 3)
ARCHIVE_FORMAT_TAR_GNUTAR = (ARCHIVE_FORMAT_TAR | 4)
ARCHIVE_FORMAT_ISO9660 = 0x40000
ARCHIVE_FORMAT_ISO9660_ROCKRIDGE = (ARCHIVE_FORMAT_ISO9660 | 1)
ARCHIVE_FORMAT_ZIP = 0x50000
ARCHIVE_FORMAT_EMPTY = 0x60000
ARCHIVE_FORMAT_AR = 0x70000
ARCHIVE_FORMAT_AR_GNU = (ARCHIVE_FORMAT_AR | 1)
ARCHIVE_FORMAT_AR_BSD = (ARCHIVE_FORMAT_AR | 2)
ARCHIVE_FORMAT_MTREE = 0x80000
ARCHIVE_FORMAT_RAW = 0x90000
ARCHIVE_FORMAT_XAR = 0xA0000
ARCHIVE_FORMAT_LHA = 0xB0000
ARCHIVE_FORMAT_CAB = 0xC0000
ARCHIVE_FORMAT_RAR = 0xD0000
ARCHIVE_FORMAT_7ZIP = 0xE0000
ARCHIVE_FORMAT_WARC = 0xF0000
ARCHIVE_FORMAT_RAR_V5 = 0x100000

ARCHIVE_EOF    = 1            # Found end of archive.
ARCHIVE_OK = 0          # Operation was successful.
ARCHIVE_RETRY = (-10)   # Retry might succeed.
ARCHIVE_WARN = (-20)    # Partial success.
ARCHIVE_FAILED = (-25)  # Current operation cannot complete.
ARCHIVE_FATAL = (-30)   # No more operations are possible.

MODE_READ = 0
MODE_WRITE = 1

DEF_BUFFER_SIZE = 16384

struct_archive = c_void_p
struct_archive_entry = c_void_p

if os.name == 'nt':
    ARCHIVEINT_LIB = windll.archiveint
    # todo: load libarchive.so on POSIX if available instead of crashing

    get_zlib_version = WINFUNCTYPE(c_char_p)(('archive_zlib_version', ARCHIVEINT_LIB))
    get_zlib_version.errcheck = lambda res, _1, _2: res.decode('utf8')

    archive_read_new = WINFUNCTYPE(struct_archive)(('archive_read_new', ARCHIVEINT_LIB))
    archive_read_support_filter_all = WINFUNCTYPE(c_int, struct_archive)(('archive_read_support_filter_all', ARCHIVEINT_LIB))
    archive_read_support_format_all = WINFUNCTYPE(c_int, struct_archive)(('archive_read_support_format_all', ARCHIVEINT_LIB))
    archive_read_support_format_raw = WINFUNCTYPE(c_int, struct_archive)(('archive_read_support_format_raw', ARCHIVEINT_LIB))
    archive_read_support_compression_all = WINFUNCTYPE(c_int, struct_archive)(('archive_read_support_compression_all', ARCHIVEINT_LIB))
    archive_read_open_filename = WINFUNCTYPE(c_int, struct_archive, c_char_p, c_int)(('archive_read_open_filename', ARCHIVEINT_LIB))
    archive_read_open_memory = WINFUNCTYPE(c_int, struct_archive, c_char_p, c_int)(('archive_read_open_memory', ARCHIVEINT_LIB))
    archive_read_next_header = WINFUNCTYPE(c_int, struct_archive, POINTER(struct_archive_entry))(('archive_read_next_header', ARCHIVEINT_LIB))
    archive_entry_pathname = WINFUNCTYPE(c_char_p, struct_archive_entry)(('archive_entry_pathname', ARCHIVEINT_LIB))
    archive_entry_pathname.errcheck = lambda res, _1, _2: res.decode('utf8') if res else ''
    archive_read_data = WINFUNCTYPE(c_int, struct_archive, c_char_p, c_int)(('archive_read_data', ARCHIVEINT_LIB))
    archive_read_data_skip = WINFUNCTYPE(c_int, struct_archive)(('archive_read_data_skip', ARCHIVEINT_LIB))
    archive_read_data_block = WINFUNCTYPE(c_int, struct_archive, POINTER(c_char_p), POINTER(c_int), POINTER(c_int))(('archive_read_data_block', ARCHIVEINT_LIB))
    archive_read_free = WINFUNCTYPE(c_int, struct_archive)(('archive_read_free', ARCHIVEINT_LIB))
    archive_read_close = WINFUNCTYPE(c_int, struct_archive)(('archive_read_close', ARCHIVEINT_LIB))
    archive_compression_name = WINFUNCTYPE(c_char_p, struct_archive_entry)(('archive_compression_name', ARCHIVEINT_LIB))
    archive_compression_name.errcheck = lambda res, _1, _2: res.decode('utf8') if res else ''
    archive_format_name = WINFUNCTYPE(c_char_p, struct_archive_entry)(('archive_format_name', ARCHIVEINT_LIB))
    archive_format_name.errcheck = lambda res, _1, _2: res.decode('utf8') if res else ''
    archive_error_string = WINFUNCTYPE(c_char_p)(('archive_error_string', ARCHIVEINT_LIB))
    archive_error_string.errcheck = lambda res, _1, _2: res.decode('utf8') if res else ''
else:
    # todo: find alternatives on Linux
    archive_read_new = None
    archive_read_support_filter_all = None
    archive_read_support_format_all = None
    archive_read_support_compression_all = None
    archive_read_open_filename = None
    archive_read_open_memory = None
    archive_read_free = None
    archive_read_next_header = None
    archive_entry_pathname = None
    archive_read_data_block = None
    archive_compression_name = None
    archive_format_name = None


class ArchiveError(ValueError): pass



class Archive:
    """
    Archive object.
    """

    def __init__(self, filename_or_data=None):
        self.mode = MODE_READ
        self.archive = None
        if filename_or_data:
            self.open_archive(filename_or_data)


    def last_error(self):
        """
        Returns the last error from libarchive.
        """
        return archive_error_string()


    def open_archive(self, filename_or_data, buffer_size=DEF_BUFFER_SIZE):
        """
        Open an archive file or buffer for reading.
        """
        self.mode = MODE_READ
        self.buffer_size = buffer_size
        self.source = filename_or_data


    def reset(self):
        """
        Reset (reopen) the archive.
        """
        self.close()
        self.archive = arc = archive_read_new()
        if archive_read_support_filter_all(arc) != ARCHIVE_OK:
            raise ArchiveError(f'Failed enabling filters: {self.last_error()})!')
        if archive_read_support_format_all(arc) != ARCHIVE_OK:
            raise ArchiveError(f'Failed enabling formats: {self.last_error()})!')
        #if archive_read_support_compression_all(arc) != ARCHIVE_OK:
        #    raise ArchiveError(f'Failed enabling compression: {self.last_error()})!')
        if type(self.source) is str:
            res = archive_read_open_filename(arc, self.source.encode('utf8'), self.buffer_size)
        else:
            res = archive_read_open_memory(arc, self.source, self.buffer_size)
        if res != ARCHIVE_OK:
            raise ArchiveError(f'Failed opening file or buffer: {res} ({self.last_error()})!')


    def close(self):
        """
        Close the archive.
        """
        if self.archive:
            archive_read_free(self.archive)
        self.archive = None


    def walk(self, callback=None):
        """
        Iterate archive member filenames returning tuples (name, entry_object).
        """
        if (not self.mode == MODE_READ) and self.source:
            raise ArchiveError('No archive is opened for reading!')
        self.reset()
        entry = struct_archive_entry()
        while archive_read_next_header(self.archive, ctypes.byref(entry)) == ARCHIVE_OK:
            entry_name = archive_entry_pathname(entry)
            if callback:
                callback(entry_name, entry)
            yield entry_name, entry



    def list_members(self):
        """
        Iterate over member names.
        """
        for name, e in self.walk():
            yield name


    def read(self, filename=None):
        """
        Read an archive member (the current one if none given); returns None if the filename is given and not present.

        Do NOT use this for large files - the data will be read to memory.
        """
        if not filename:
            return self.read_crt_entry()
        for name, e in self.walk():
            if name == filename:
                return self.read_crt_entry()


    def read_crt_entry(self):
        """
        Read the current archive entry.
        """
        if (not self.mode == MODE_READ) and self.archive:
            raise ArchiveError('No archive is opened for reading!')
        chunk = c_char_p()
        chunk_size = c_int()
        offset = c_int(0)
        lst = []
        while 1:
            res = archive_read_data_block(self.archive, byref(chunk), byref(chunk_size), byref(offset))
            offset.value += chunk_size.value
            if res == ARCHIVE_EOF:
                break
            elif res != ARCHIVE_OK:
                raise ArchiveError(f'Failed reading current archive entry: {res} ({self.last_error()})!')
            lst.append(chunk.value[:chunk_size.value])
        return b''.join(lst)


    def get_format(self):
        """
        Returns the format of the current archive.
        """
        if (not self.mode == MODE_READ) and self.source:
            raise ArchiveError('No archive is opened for reading!')
        if not self.archive:
            self.reset()
        return archive_compression_name(self.archive)


    def get_entry_format(self):
        """
        Returns the format of the current archive entry.
        """
        if (not self.mode == MODE_READ) and self.archive:
            raise ArchiveError('No archive is opened for reading!')
        return archive_format_name(self.archive)



"""
Example:

    a = Archive('test.zip')
    print(a.get_format())
    for name in a.list_members():
        print(name, a.get_entry_format())
        if name == 'extractme.ext':
            data = a.read()
            open(name, 'wb').write(data)
    print(a.read('test.py'))
    a.close()
"""
