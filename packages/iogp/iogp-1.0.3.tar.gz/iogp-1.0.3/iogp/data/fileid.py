"""
iogp.data.fileid: File identification APIs.

Author: Vlad Topan (vtopan/gmail)
"""

import re
import struct


HEADER_SIZE = 8192

FT_UNKNOWN = 'unknown'
FT_EMPTY = 'empty'

FT_REGEX = {
    # archive
    'svnz':         rb'^7z\xBC\xAF\x27\x1C',    # should be 7z, but Python regex named groups cannot contain digits
    'ace':          rb'^.{3}\0{3}.\*\*ACE\*\*\x14\x14',
    'alz':          rb'^ALZ\x01',
    'arj':          rb'^\x60\xEA',
    'bz2':          rb'^BZh',
    'cab_ishield':  rb'^ISc\x28',
    'cab_ms':       rb'^MSCF',
    'compressed':   rb'^(SZDD|KWAJ)\x88\xF0\x27(\x33|\xD1)',
    'crx':          rb'^Cr24',
    'deb':          rb'^!<arch>\.',
    'gz':           rb'^\x1F\x8B\x08',
    'lh_arc':       rb'^\x1A[\x02-\x04\x08\x09]',
    'lz':           rb'^LZIP',
    'lz4':          rb'^\x04"M\x18',
    'lzh':          rb'^..-lh',
    'lzs':          rb'^EDILZSS',
    'rar':          rb'^Rar!\x1A\x07',
    'rpm':          rb'^\xED\xAB\xEE\xDB',
    'tar':          rb'^.{256}\0ustar|^[\x20-\x7E].{64}\0{31}\0{4}([0-7 ]{6}[0-7 \0]\0){3}.{368}\0',
    'tar_z':        rb'^\x1F\x9d\x90',
    'xz':           rb'^\xFD7zXZ\0',
    'z':            rb'^\x13\x5De\x8C:\x01\x02\x00',
    'zlib':         rb'^\x78[\x01\x20\x5E\x7D\x9C\xBB\xDA\xF9]',
    'zoo':          rb'^ZOO ',
    # audiovideo
    'asf':          rb'^\x30\x26\xB2\x75\x8E\x66\xCF\x11',
    'flac':         rb'^fLaC',
    'mid':          rb'^MThd',
    'mkv':          rb'^\x1A\x45\xDF\xA3',
    'mp3':          rb'^\xFF[\xF2\xF3\xFB]|^ID3',
    'mpg':          rb'^\0\0\x01[\xBA\xB3]',
    'ogg':          rb'^OggS',
    'tgp':          rb'^ftyp3g',    # should be 3gp, but Python regex named groups cannot contain digits
    # disk
    'dmg':          rb'x\x01s\x0Dbb`',
    'iso':          rb'^CD001',
    'nes':          rb'^NES\x1A',
    'vmdk':         rb'^KDM',
    # doc
    'chm':          rb'^ITSF\x03\0{3}`\0{3}',
    'djvu':         rb'^AT&TFORM.{4}DJV',
    'doc':          rb'^\xD0\xCF\x11\xE0.{508}\xEC\xA5\xC1\0',
    'dwg':          rb'^AC(10|2\.)',
    'eml':          rb'^Received:',
    'html':         rb'(?i:^<(html|!doctype html))',
    'msg':          rb'^\xD0\xCF\x11\xE0.{508}' + 'Root Ent'.encode('utf16'),
    'one':          rb'\xE4\x52\x5C\x7B\x8C\xD8\xA7\x4D\xAE\xB1\x53\x78\xD0\x29\x96\xD3',
    'pdf':          rb'^%PDF-1',
    'ppt':          rb'^\xD0\xCF\x11\xE0.{508}(\x0F\0\xE8\x03|\xA0\x46\x1D\xF0|\0\x6E\x1E\xF0)',
    'ps':           rb'^\x04?%!PS',
    'rtf':          rb'^\{\\rtf',
    'swf':          rb'^[CF]WS',
    'wks':          rb'^\0{2}\x02\0\x04',
    'wordperfect':  rb'^\xFFWPC',
    'wri':          rb'^[12]\xBE\0{3}\xAB\0{2}',
    'xls':          rb'^\xD0\xCF\x11\xE0.{508}\x09\x08\x10\0\0\x06\x05\0',
    'xls_20':       rb'^\x09\0\x04\0\x02\0',
    'xml':          rb'^(?i:<\?xml)',
    # executable
    'class':        rb'^\xCA\xFE\xBA\xBE',
    'dex':          rb'^dex\x0A',
    'elf':          rb'^\x7FELF',
    'fox':          rb'^\xFB{2}.\x02',
    'lib_basic':    rb'^\xF0\x0D\0\0',
    'luac':         rb'^\x1BLua',
    'macho32':      rb'^\xCE\xFA\xED\xFE',
    'macho64':      rb'^\xCF\xFA\xED\xFE',
    'obj_coff':     rb'^L\x01',
    'pyc':          rb'^([\x6D\xB3\xD1]\xF2|\x03\xF3|[\x3B\x4F\x6C\x9E\xEE]\x0C|[\x16\x33\x42\x55]\x0D)\x0D\x0A',
    'wasm':         rb'^\0asm',
    # image
    'bmp':          rb'^BM',
    'bmp_ddb':      rb'^\x02\0{3}',
    'cdr':          rb'^WLe\0',
    'exr':          rb'^v/1\x01',
    'gif':          rb'^GIF8[79]',
    'ico':          rb'^\0\0(\x01\0|\x02\0)[\x01-\x04]\0',
    'jpg':          rb'^\xFF\xD8\xFF',
    'pcx':          rb'^\x0A[\x00-\x05]',
    'png':          rb'^\x89PNG\x0D\x0A\x1A\x0A',
    'psd':          rb'^8BPS',
    'svg':          rb'^<svg\s',
    'tif':          rb'^(II\x2A\0|MM\0\x2A)',
    'wmf':          rb'^\xD7\xCD\xC6\x9A',
    'wmf_3X':       rb'^\x01\0\x09\0',
    # installer files
    'ins':          rb'^(\xB8\xC9\x0C\0|\xFF{2}\x0C\0\x14\0\x34\x12)',
    'iss':          rb'^\[InstallSHIELD',
    'pkg':          rb'^\x4A\xA3',
    'stirling_exe': rb'^\x2A\xAB\x79\xD8\0\x01',
    # crypto
    'openssh_pub_key':  rb'ssh-\w+ [\w/+=]{32,}',
    'openssh_prv_key':  rb'-----BEGIN OPENSSH PRIVATE KEY-----',
    'pkcs8_prv_key':  rb'-----BEGIN PRIVATE KEY-----',
    'pkcs8_pub_key':  rb'-----BEGIN PUBLIC KEY-----',
    'pkcs1_prv_key':  rb'-----BEGIN [RD]SA PRIVATE KEY-----',
    'pkcs1_pub_key':  rb'-----BEGIN [RD]SA PUBLIC KEY-----',
    'ssh_rfc_prv_key':  rb'----[- ]BEGIN SSH2 PRIVATE KEY[- ]----',
    'ssh_rfc_pub_key':  rb'----[- ]BEGIN SSH2 PUBLIC KEY[- ]----',
    # misc
    'der':          rb'^0\x82',
    'evtx':         rb'^ElfFile',
    'hlp':          rb'^\x3F_\x03\0',
    'i64':          rb'^IDA2',
    'kdb':          rb'^7H\x03\x02\0{4}X509KEY',
    'lnk':          rb'^L\0{3}\x01\x14\x02\0{5}\xc0\0{6}F',
    'otf':          rb'^OTTO',
    'pcap':         rb'^\xA1\xB2\xC3\xD4|\xD4\xC3\xB2\xA1',
    'pcapng':       rb'^\x0A\x0D\x0D\x0A',
    'pdb':          rb'^Microsoft C/C\+\+ (program database|MSF) [\d\.]+\r\n\x1A',
    'pdb_ida':      rb'^IDA1',
    'pfb':          rb'^\x80\x01',
    'pgp':          rb'^(\x85\x01\x0C\x03|\x8C[\x04\x0C\x0D]\x04]|-----BEGIN PGP M)',
    'r1cs':         rb'^r1cs',
    'sqlite':       rb'^SQLite format',
    'ttc':          rb'^ttcf',
    'ttf':          rb'^\0\x01\0{3}.{3}\0[\x03\x04]\0.(OS/2|LTSH|cmap|DSIG|FFTM|GDEF|Feat|GPOS|ASCP|COLR|BASE|EBDT).{4}([\0\x01].{3}){2}[/A-Za-z0-9 ]{4}',
    # script
    'reg4':         rb'^REGEDIT4',
    'reg5':         rb'^\xFF\xFE' + 'Windows Registry Editor Version 5'.encode('utf16'),
    'script_posix': rb'^#!/[\w/ ]+',
    # keep at the end
    'text_utf8':    rb'^\xEF\xBB\xBF',
    'text_ascii':   rb'^[\x09\x0A\x0D\x20-\x7E]+\x1A?$',
    }
FULL_RX = re.compile(b'|'.join(b'(?P<%s>%s)' % (k.encode('utf8'), v) for k, v in FT_REGEX.items()), re.S)
FT_SUBTYPE_REGEX = {
    'svg':          rb'^(?i:<\?xml [^>]+\?>\s*(<\!(DOCTYPE|--)[^>]*>\s*)*<svg\s)',
    'vcproj':       rb'^.{0,50}<VisualStudioProject',
}
SUBTYPE_RX = re.compile(b'|'.join(b'(?P<%s>%s)' % (k.encode('utf8'), v) for k, v in FT_SUBTYPE_REGEX.items()), re.S)

FT_CATEGORY = {
    'audiovideo': ('3gp', 'asf', 'avi', 'flac', 'mid', 'mkv', 'mp3', 'mpg', 'ogg', 'wav',),
    'archive': ('7z', 'alz', 'arj', 'bz2', 'cab_ms', 'cab_ishield','compressed', 'crx', 'deb', 'dmg', 'egg', 'gz', 'jar',
            'lh_arc', 'lz', 'lz4', 'lzh', 'lzs', 'rar', 'rpm','tar', 'tar_z', 'xz', 'z', 'zip', 'zlib', 'zoo',),
    'disk': ('dmg', 'iso', 'nes', 'vmdk',),
    'document': ('chm', 'djvu', 'doc', 'dwg', 'eml', 'html', 'odt', 'one', 'pdf', 'ppt', 'ps', 'rtf', 'swf', 'text_ascii',
            'text_utf8', 'wks', 'wordperfect', 'wri', 'xls', 'xls_20', 'xml',),
    'executable': ('class', 'coff', 'dex', 'elf', 'fox', 'lib_basic', 'luac', 'macho32', 'macho64', 'mz', 'ne', 'obj_coff',
            'pe', 'pe+', 'wasm',),
    'image': ('ani', 'bmp', 'bmp_ddb', 'cdr', 'gif', 'ico', 'jpg', 'pcx', 'png', 'psd', 'tif', 'webp', 'wmf', 'wmf_3X',),
    'installers': ('ins', 'inst_exe', 'iss', 'pkg', 'stirling_exe',),
    'misc': ('der', 'fon', 'hlp', 'i64', 'kdb', 'lnk', 'otf', 'pcap', 'pcapng', 'pdb', 'pdb_ida', 'pfb', 'pgp', 'riff',
            'sqlite', 'ttc', 'ttf',),
    'script': ('reg4', 'reg5',),
    FT_UNKNOWN: (FT_UNKNOWN, FT_EMPTY, 'docfile_ms',),
    }
FT_CAT_MAP = {vv:k for k, v in FT_CATEGORY.items() for vv in v}

FT_EXT_MAP = {
    'elf': '',
    'macho32': 'so',
    'macho64': 'so',
    'mz': 'exe',
    'ne': 'exe',
    'pe': 'exe',
    'pe+': 'exe',
    'reg4': 'reg',
    'reg5': 'reg',
    'script_awk': 'awk',
    'script_node': 'js',
    'script_posix': '',
    'script_python': 'py',
    'script_perl': 'pl',
    'script_sh': 'sh',
    'sqlite': 'db',
    'stirling_exe': 'ex_',
    'tar_z': 'tar.z',
    'text_ascii': 'txt',
    'text_utf8': 'txt',
    'wordperfect': 'wpd',
    'thumbsdb': 'db',
    }

FT_2_MIME = {
    '7z': 'application/x-7z-compressed',
    'aac': 'audio/aac',
    'avi': 'video/x-msvideo',
    'azw': 'application/vnd.amazon.ebook',
    'bin': 'application/octet-stream',
    'bz2': 'application/x-bzip2',
    'css': 'text/css',
    'csv': 'text/csv',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'epub': 'application/epub+zip',
    'gif': 'image/gif',
    'gz': 'application/gzip',
    'html': 'text/html',
    'ico': 'image/vnd.microsoft.icon',
    'ics': 'text/calendar',
    'jar': 'application/java-archive',
    'jpg': 'image/jpeg',
    'js': 'text/javascript',
    'json': 'application/json',
    'mp3': 'audio/mpeg',
    'mp4': 'video/mp4',
    'odp': 'application/vnd.oasis.opendocument.presentation',
    'ods': 'application/vnd.oasis.opendocument.spreadsheet',
    'odt': 'application/vnd.oasis.opendocument.text',
    'ogg': 'audio/ogg',
    'pdf': 'application/pdf',
    'php': 'application/x-httpd-php',
    'png': 'image/png',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'rar': 'application/vnd.rar',
    'rtf': 'application/rtf',
    'sh': 'application/x-sh',
    'svg': 'image/svg+xml',
    'tar': 'application/x-tar',
    'tiff': 'image/tiff',
    'ttf': 'font/ttf',
    'txt': 'text/plain',
    'wav': 'audio/wav',
    'weba': 'audio/webm',
    'webm': 'video/webm',
    'webp': 'image/webp',
    'xhtml': 'application/xhtml+xml',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'xml': 'application/xml',
    'zip': 'application/zip',
}
MIME_2_FT = {v: k for k, v in FT_2_MIME.items()}


def get_file_type(source):
    """
    Identify the type of a file (or `bytes` buffer).

    :param source: File handle, filename or bytes buffer.
    """
    if hasattr(source, 'read'):
        header = source.read(HEADER_SIZE)
    elif type(source) == str:
        header = open(source, 'rb').read(HEADER_SIZE)
    else:
        header = source[:HEADER_SIZE]
    if len(header) == 0:
        return FT_EMPTY
    if header[:2] == b'MZ':
        if len(header) >= 0x100:
            elfanew = struct.unpack('<L', header[0x3C:0x40])[0]
            if elfanew + 8 < len(header):
                if header[elfanew:elfanew + 4] == b'PE\0\0':
                    machine = header[elfanew + 4:elfanew + 6]
                    if machine == b'\x64\x86':
                        return 'pe+'
                    elif machine == b'\x4c\x01':
                        return 'pe'
                    else:
                        return 'coff'
            ne_offs = struct.unpack('<H', header[0x3C:0x3E])[0]
            if ne_offs + 0x30 < len(header):
                if header[ne_offs:ne_offs + 2] == b'NE':
                    if b'FONTRES' in header[ne_offs + 0x80:ne_offs + 0x140]:
                        # todo: parse NE header
                        return 'fon'
                    return 'ne'
        return 'mz'
    elif header[:4] == b'RIFF':
        mark = header[8:12]
        if mark == b'WAVE':
            return 'wav'
        elif mark == b'AVI ':
            return 'avi'
        elif mark == b'ACON':
            return 'ani'
        elif mark == b'WEBP':
            return 'webp'
        else:
            return 'riff'
    elif header[:2] == b'PK':
        if b'META-INF/MANIFEST' in header and b'.class' in header:
            return 'jar'
        elif b'mimetypeapplication/epub+zip' in header[:0x40]:
            return 'epub'
        elif b'mimetypeapplication/vnd.oasis.opendocument.tex' in header[:0x50]:
            return 'odt'
        elif b'EGG-INFO/' in header[:0x40]:
            return 'egg'
        elif b'[Content_Types].xml' in header[:0x50]:
            # M$ Office zipped XML format
            if b'\x01xl/_rels/' in header:
                return 'xlsx'
            if b'\x01word/_rels/' in header:
                return 'docx'
            return 'office-zip'
        return 'zip'
    m = FULL_RX.search(header)
    if m:
        for k in FT_REGEX:
            if m.group(k):
                match = m.group()
                if k == 'tgp':
                    k = '3gp'
                elif k == 'svnz':
                    k = '7z'
                elif k in ('xml',):
                    if sm := SUBTYPE_RX.search(header):
                        for sk in FT_SUBTYPE_REGEX:
                            if sm.group(sk):
                                k = sk
                                break
                elif k == 'script_posix':
                    for e in (b'perl', b'python', b'make', b'awk', b'wish', b'node'):
                        if re.search(rb'[ /]%s($|\W)' % e, match):
                            e = e.decode('utf8')
                            return 'script_' + {'wish': 'tcl'}.get(e, e)
                    if re.search(rb'/[tck]?sh(\W|$)', match):
                        return 'script_sh'
                return k
    if header[:4] == b'\xD0\xCF\x11\xE0':
        return 'docfile_ms'
    if len(header) == 0x200 and header[0x1FE:0x200] == b'\x55\xAA':
        return 'bootsector_x86'
    return FT_UNKNOWN


def get_ft_category(filetype):
    """
    Returns the category of the given filetype.
    """
    if filetype.startswith('script_'):
        return 'script'
    return FT_CAT_MAP.get(filetype, FT_UNKNOWN)


def get_ft_ext(filetype):
    """
    Returns the most common file extension for the given filetype (or FT_UNKNOWN).
    """
    ext = FT_EXT_MAP.get(filetype, filetype)
    if '_' in ext and not ext.endswith('_'):
        ext = ext.split('_', 1)[0]
    return ext
