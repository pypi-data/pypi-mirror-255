#!/usr/bin/env python3
"""
iogp unit tests.

Author: vtopan / gmail
"""
import iogp
import os
import time
import argparse


argp = argparse.ArgumentParser(description='iogp tester')
argp.add_argument('-N', '--network', help='include network-dependent tests', action='store_true') 
args = argp.parse_args() 

test_zip_data = open('test.zip', 'rb').read()


# iogp.archive

a = iogp.data.Archive('test.zip')
assert ['test'] == list(a.list_members())
assert b'test' == a.read('test')
a.close()

# iogp.carve

delta = 10
emb = list(iogp.data.extract_embedded_files(b'X' * delta + test_zip_data + b'X' * delta))
assert len(emb) == 1
assert emb[0][0] == delta
assert emb[0][1] == len(test_zip_data)

# iogp.ds

assert iogp.data.dict_to_AttrDict({'test': []}).test == []

# iogp.fileid

assert iogp.data.get_file_type(test_zip_data) == 'zip'

if os.name == 'nt':
    assert iogp.data.get_file_type(r'c:\windows\regedit.exe') == 'pe+'  # expect Win 64
elif os.name == 'posix':
    assert iogp.data.get_file_type('/bin/sh') == 'elf'

# iogp.str

assert iogp.data.ellipsis('0123456789', 9) == '0123[...]'

# iogp.db

cache = iogp.db.DataCache(max_age=1)
cache['test'] = 'testdata'
assert cache['test'] == 'testdata'
time.sleep(1)
assert cache.get_age('test') > 0.5
assert cache['test'] is None

# iogp.net

assert b'Cloudflare' in iogp.net.download('https://1.1.1.1/')

# iogp.win

if os.name == 'nt':
    assert iogp.win.get_window_size() > (100, 100)

print('All unit tests were successful!')
