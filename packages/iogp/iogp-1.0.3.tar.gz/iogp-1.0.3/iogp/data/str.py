"""
iogp.data.str: Strings.

Author: Vlad Topan (vtopan/gmail)
"""
import ast
import codecs
import datetime
from logging import error
import math
import re
import time

from .map437 import CP437_TO_UNICODE, UNICODE_TO_CP437


NUM_MODS = 'KMBTQ'


def ellipsis(s, size):
    """
    Trim a string to a maximum size, add an ellipsis ("[...]") if trimmed.
    """
    if len(s) > size:
        s = s[:size - 5] + '[...]'
    return s


def parse_num(s):
    """
    Extract the value from a formatted number.
    """
    if s in ('N/A', None, '-', ''):
        return 0    # None
    if s == 0:
        return 0
    if re.search(r'^-?[,\.\d]+%$', s):
        # percent => normalize to 0.0..1.0
        return ast.literal_eval(s.replace(',', '').rstrip('%')) / 100
    s = s.replace(',', '')
    sign = 1
    if s[0] == '(' and s[-1] == ')':
        sign = -1
        s = s.strip('()')
    if s[-1] in NUM_MODS:
        value = int(float(s[:-1]) * (10 ** (3 * (NUM_MODS.index(s[-1]) + 1))))
    elif s[-1] in NUM_MODS.lower():
        value = int(float(s[:-1]) * (10 ** (3 * (NUM_MODS.lower().index(s[-1]) + 1))))
    else:
        try:
            value = float(s) if '.' in s else int(s)
        except ValueError:
            error(f'Failed parsing {s} as float/int!')
            value = 0
    value = sign * value
    return value


def parse_percent(text):
    """
    Extract a percent float (0.0 .. 1.0) from text (with or without %).
    """
    return float(text.strip().strip('%')) / 100


def format_size(size):
    """
    Format a size in bytes.
    """
    for i, c in enumerate(('P', 'T', 'G', 'M', 'K', '')):
        v = (2 ** 10) ** (5 - i)
        if v <= size:
            s = str(int(size * 100 / v))
            s = s[:-2] if s.endswith('00') else s[:-2] + '.' + s[-2:]
            return s + f' {c}B'
    return '0B'


def format_num(num):
    """
    Format a (potentially large) number.
    """
    neg, num = int(num < 0), abs(num)
    for i, c in enumerate(list(reversed(NUM_MODS)) + ['']):
        v = 1000 ** (len(NUM_MODS) - i)
        if v <= num:
            s = str(int(num * 100 / v))
            s = s[:-2] if s.endswith('00') else s[:-2] + '.' + s[-2:]
            return (neg * '-') + s + c
    return f'{num:.3f}'


def format_date(ts):
    """
    Format a date, datetime or timestamp as a date.
    """
    if type(ts) in (datetime.datetime, datetime.date):
        return ts.strftime('%Y.%m.%d')
    if type(ts) in (int, float):
        ts = time.localtime(ts)
    return time.strftime('%Y.%m.%d', ts)


def format_datetime(ts):
    """
    Format a datetime or timestamp as a date + time (no seconds).
    """
    if type(ts) is datetime.datetime:
        return ts.strftime('%H:%M, %Y.%m.%d')
    if type(ts) in (int, float):
        ts = time.localtime(ts)
    return time.strftime('%H:%M, %Y.%m.%d', ts)


def format_percent(v):
    """
    Format a value as a percent.
    """
    return f'{(v or 0) * 100:.2f}%'


def int_to_bytes(val, size=None, byteorder='big'):
    """
    Convert an integer to a `bytes` string.

    This does the same thing as PyCryptodome's Crypto.Util.Number.long_to_bytes().

    :param byteorder: 'big' or 'little'.
    """
    size = size or int(math.ceil((val.bit_length() + 7) >> 3))
    res = val.to_bytes(size, byteorder=byteorder)
    return res


def bytes_to_int(val, byteorder='big'):
    """
    Convert a `bytes` string to an integer.

    This does the same thing as PyCryptodome's Crypto.Util.Number.bytes_to_long().

    :param byteorder: 'big' or 'little'.
    """
    res = int.from_bytes(val, byteorder=byteorder)
    return res


def dump_dict(title, d, indent=0):
    """
    Pretty-print dictionary whose values are other dicts, lists or basic types.
    """
    lines = []
    if title:
        lines.append(f'{indent * "  "}- {title}:')
    for k, v in d.items():
        if type(v) is dict:
            lines.append(dump_dict(k, v, indent + 1))
        elif type(v) is list:
            lines.append(f'{indent * "  "}  - {k}:')
            for i, e in enumerate(v):
                lines.append(dump_dict(f'#{i}', e, indent + 2))
        else:
            lines.append(f'{indent * "  "}  - {k}: {v}')
    return '\n'.join(lines)


def to_hex(data, wrap=None, truncate=None, sep=' '):
    """
    Encode `bytes` (or `str`) string as hex.

    :param wrap: Wrap at this many characters (rounded to 3).
    :param truncate: If longer than this many characters, truncate and append an ellipsis.
    """
    if isinstance(data, str):
        data = data.encode('ascii')
    data = data.hex()
    data = sep.join(a + b for a, b in zip(data[::2], data[1::2]))
    if truncate and len(data) > truncate:
        return data[:truncate] + '[...]'
    mul = 2 + len(sep)
    if wrap:
        wrap = wrap // mul * mul
        data = '\n'.join(data[i:i + wrap].rstrip(' ') for i in range(0, len(data), wrap))
    return data


def decode_cp437(data: bytes):
    """
    Decode bytes to str based on the CP437 DOS font / codepage.
    """
    return ''.join(CP437_TO_UNICODE[e] for e in data)


def clean_filename(filename, rep='_'):
    """
    Remove all potentially problematic symbols from a filename.
    """
    filename = re.sub(r'[^a-z0-9_\., ~@()=+-]+', rep, filename, flags=re.I).strip().rstrip(' .')
    return filename
