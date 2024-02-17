"""
iogp.db.cache: Generic DB-based URI caching objects.

Author: Vlad Topan (vtopan/gmail)
"""

from .sqlite import DB

import dbm
import os
import sys
import pickle
import marshal
import zlib
import time
import collections
try:
    import yaml
except ImportError:
    yaml = None
import json


DEF_DB_FILENAME = '.obj_cache.db'
DEF_MAX_AGE = 12 * 3600

ENC_MODE_ZLIB = 0x0001
ENC_MODE_PICKLE = 0x0002
ENC_MODE_MARSHAL = 0x0004
ENC_MODE_YAML = 0x0008
ENC_MODE_JSON = 0x0010
ENC_MODE_PZ = ENC_MODE_PICKLE | ENC_MODE_ZLIB
ENC_MODE_MARZ = ENC_MODE_MARSHAL | ENC_MODE_ZLIB
ENC_MODE_YZ = ENC_MODE_YAML | ENC_MODE_ZLIB
ENC_MODE_JZ = ENC_MODE_JSON | ENC_MODE_ZLIB

VALID_ENCODING_MODES = [
    ENC_MODE_ZLIB, ENC_MODE_PZ, ENC_MODE_PICKLE, ENC_MODE_YAML,
    ENC_MODE_MARSHAL, ENC_MODE_MARZ, ENC_MODE_YZ, ENC_MODE_JZ, ENC_MODE_JSON
    ]

CACHE_ALWAYS = -1  # always cache
CACHE_ONLY = -2  # only return from cache

BE_SQLITE = 1
BE_DBM = 2
BACKENDS = {
    'sqlite': BE_SQLITE,
    'dbm': BE_DBM,
    }


TABLES = {
    'cache': 'uri TEXT PRIMARY KEY, data BLOB, ts INT, enc_mode INT',
    }
INDEXES = {
    'cache': ['uri'],
    }


def ObjCache(filename=None, timing=0, **kargs):
    """
    Wrapper over DataCache which generates an automatic filename based on the main script name.

    Pass max_age=None to prevent items from ever expiring.
    """
    if not filename:
        filename = '_%s_obj.cache' % (os.path.basename(sys.argv[0])).split('.', 1)[0][:12]
    return DataCache(filename, timing=timing, **kargs)



class DataCache(object):
    """
    Generic URI-based data/object caching, backed by dbm or an SQLITE db.

    Can be used as a dictionary.

    :param encoding: Used for all non-string data; must be one of the ENC_MODE_* constants.
    :param max_age: 0 or negative value means "don't expire", otherwise number of seconds until entry expires.
    :param backend: 'sqlite' or 'dbm'.
    :param timing: Set to true to enable timing operations for debug purposes.
    """

    def __init__(self, filename=None, max_age=DEF_MAX_AGE, encoding=ENC_MODE_MARZ, timing=0, backend='sqlite',
                **kwargs):
        self.backend = BACKENDS[backend]
        self.encoding = kwargs.pop('obj_enc_mode', encoding)
        self.max_age = max_age
        self.filename = filename or DEF_DB_FILENAME
        self._db = None
        self._kwargs = kwargs
        self._connected = False
        self.timing = timing
        self.times = collections.defaultdict(lambda:list((0, 0)))
        self._del_count = 0


    @property
    def db(self):
        """
        Database object.
        """
        if not self._connected:
            if os.path.dirname(self.filename) and not os.path.isdir(os.path.dirname(self.filename)):
                os.makedirs(os.path.dirname(self.filename))
            # print('Connecting to DB [%s]...' % self.filename)
            if self.backend == BE_SQLITE:
                self._db = DB(self.filename, **self._kwargs)
                self._db.create_tables(TABLES)
                self._db.create_indexes(INDEXES)
            else:
                self._db = dbm.open(self.filename, 'c', **self._kwargs)
            self._connected = True
        return self._db


    def exists(self, uri):
        """
        Checks if a URI is present in the cache.
        """
        if self.backend == BE_SQLITE:
            res = self.db.fetchone("SELECT ts FROM cache WHERE uri = ?", (uri,))
        else:
            res = self.db.get(uri, None)
        if res and self.max_age and self.max_age > 0 and (time.time() - res[0] > self.max_age):
            res = None
        return bool(res)


    def get(self, uri, max_age=None):
        """
        Get cached data for the given URI.
        """
        t0 = time.time()
        if max_age is None:
            max_age = self.max_age
        if self.backend == BE_SQLITE:
            res = self.db.fetchone("SELECT data, ts, enc_mode FROM cache WHERE uri = ?", (uri,))
            if res:
                res, ts, enc = res
        else:
            res, enc = self.db.get(uri, None), self.encoding
        if res:
            try:
                res = decode_data(res, enc)
            except Exception as e:
                # data corruption
                print('[!] Corrupted data for URI [%s]: %s!' % (uri, e))
                # del self[uri]
                res = None
            if self.backend == BE_DBM:
                ts, res = res[1], res[0]
        if res and max_age and max_age > 0 and time.time() - ts > max_age:
            res = None
        if self.timing:
            self.times['get'][0] += 1
            self.times['get'][1] += time.time() - t0
        return res


    def get_age(self, uri):
        """
        Returns the age (in seconds) of an URI if present in the cache (or None).
        """
        if self.backend == BE_SQLITE:
            res = self.db.fetchone("SELECT ts FROM cache WHERE uri = ?", (uri,))
        else:
            res = self.db.get(uri, None)
        return time.time() - res[0] if res else None


    def __contains__(self, uri):
        return self.exists(uri)


    def __getitem__(self, uri, *args):
        res = self.get(uri)
        return res


    def __delitem__(self, uri):
        self._del_count += 1
        if self.backend == BE_SQLITE:
            self.db.execute("DELETE FROM cache WHERE uri = ?", (uri,))
        else:
            del self.db[uri]


    def __setitem__(self, uri, data):
        t0 = time.time()
        enc_mode = self.encoding
        if self.backend == BE_SQLITE:
            del self[uri]
            data = encode_data(data, enc_mode)
            try:
                self.db.execute("INSERT INTO cache(uri, ts, data, enc_mode) VALUES (?, ?, ?, ?)",
                    (uri, int(time.time()), data, enc_mode))
            except Exception as e:
                print(f'!!! insert failed for URI {uri}: {e}')
                raise
        else:
            self.db[uri] = encode_data([data, int(time.time()), enc_mode], enc_mode)
        if self.timing:
            self.times['set'][0] += 1
            self.times['set'][1] += time.time() - t0


    def __iter__(self):
        if self.backend == BE_SQLITE:
            self.__crt = None
            return self
        else:
            return self.db.__iter__()


    def __next__(self):
        return self.next()


    def next(self):
        """
        Iterator helper.
        """
        if self.__crt is None:
            # first item
            self.__crt = self.db.fetchvalue("SELECT uri FROM cache ORDER BY uri ASC LIMIT 1")
        else:
            # next
            self.__crt = self.db.fetchvalue("SELECT uri FROM cache WHERE uri > ? ORDER BY uri ASC LIMIT 1",
                    (self.__crt,))
        if not self.__crt:
            raise StopIteration()
        return self.__crt


    def close(self, vacuum=0):
        """
        Close DB connections (if any).
        """
        if self.backend == BE_SQLITE and vacuum and self._del_count:
            t0 = time.time()
            self.db.vacuum()
            if self.timing:
                self.times['vacuum'][0] += 1
                self.times['vacuum'][1] += time.time() - t0


    def dump_timing(self):
        """
        Print timing (debug) information.
        """
        if not self.times:
            print('No cache timing data!')
            return
        print('Cache timing data:')
        for k, v in self.times.items():
            print('%-8s %6d %7.2fs' % (k, v[0], v[1]))


    def keys(self):
        if self.backend == BE_DBM:
            return self.db.keys()
        return [x[0] for x in self.db.fetchall("SELECT uri FROM cache ORDER BY uri ASC")]


    def __len__(self):
        if self.backend == BE_DBM:
            return len(self.db)
        return self.db.fetchone("SELECT count(1) FROM cache")[0]


    def items(self):
        for k in self.keys():
            yield (k, self[k])



class DataStore(DataCache):
    """
    Data store which Caches part of the data in memory.
    """

    def __init__(self, filename=None, mcnt=10000, free=0.01, max_age=0, **kwargs):
        max_age = kwargs.pop('max_age', max_age)
        super().__init__(filename, max_age=max_age, **kwargs)
        self.mcnt = mcnt
        self.free = free if type(free) == int else int(mcnt * free)
        self._mcache = {}


    def get(self, uri, max_age=None):
        """
        Overloads `DataCache.get()` to implement in-memory caching.
        """
        if uri in self._mcache:
            e = self._mcache[uri]
            if not max_age or (time.time() - e[1] < max_age):
                return e[0]
        res = super().get(uri, max_age=max_age)
        self._mcache[uri] = [res, time.time()]
        if len(self._mcache) >= self.mcnt:
            remove = sorted(self._mcache.items(), key=lambda e:e[1][1])[:self.free]
            # print('RM: %d' % len(remove))
            for k, v in remove:
                del self._mcache[k]
        return res


    def __setitem__(self, uri, data):
        self._mcache[uri] = [data, time.time()]
        super().__setitem__(uri, data)



def encode_data(data, enc_mode):
    """
    Encodes and/or compresses data for serialization.

    :param data: `bytes` buffer.
    :param enc_mode: one or more `ENC_MODE_*` flags.
    """
    if enc_mode not in VALID_ENCODING_MODES:
        raise ValueError('Invalid encoding mode [%s]!' % enc_mode)
    if enc_mode & ENC_MODE_YAML:
        data = yaml.dumps(data)
    if enc_mode & ENC_MODE_JSON:
        data = json.dumps(data).encode('ascii')
    if enc_mode & ENC_MODE_PICKLE:
        data = pickle.dumps(data)
    if enc_mode & ENC_MODE_MARSHAL:
        data = marshal.dumps(data)
    if enc_mode & ENC_MODE_ZLIB:
        data = zlib.compress(data, level=zlib.Z_BEST_SPEED)
    return data


def decode_data(data, enc_mode):
    """
    Decodes and/or decompresses data for deserialization.

    :param data: `bytes` buffer.
    :param enc_mode: one or more `ENC_MODE_*` flags (must match the flags passed to `encode_data`).
    """
    if enc_mode not in VALID_ENCODING_MODES:
        raise ValueError('Invalid encoding mode [%s]!' % enc_mode)
    if enc_mode & ENC_MODE_ZLIB:
        data = zlib.decompress(data)
    if enc_mode & ENC_MODE_JSON:
        data = json.loads(data.decode('ascii'))
    if enc_mode & ENC_MODE_PICKLE:
        data = pickle.loads(data)
    if enc_mode & ENC_MODE_MARSHAL:
        data = marshal.loads(data)
    return data

