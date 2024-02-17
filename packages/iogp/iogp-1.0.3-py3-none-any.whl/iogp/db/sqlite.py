"""
iogp.db.sqlite: SQLITE wrapper implementing the GenDBObj interface in `iogp.dbobj`.

Author: Vlad Topan (vtopan/gmail)
"""

from .dbobj import GenDBObj

import re
import ctypes
import time
import zlib
import io
import sqlite3


SQLITE_OK = 0
SQLITE_ERROR = 1
SQLITE_BUSY = 5
SQLITE_LOCKED = 6

SQLITE_OPEN_READONLY = 1
SQLITE_OPEN_READWRITE = 2
SQLITE_OPEN_CREATE = 4


DEF_ID_KEY = 'id'
DEF_INT_KEY = 'rowid'
ISYM = '?'
DEF_PK_TYPE = 'INT PRIMARY KEY ASC'



class DB(GenDBObj):
    """
    SQLITE DB object.
    """


    def __init__(self, path=None, serialized=False, **kwargs):
        super().__init__(serialized=serialized, **kwargs)
        self.DEF_ID_KEY = DEF_ID_KEY
        self.DEF_INT_KEY = DEF_INT_KEY
        self.ISYM = ISYM
        self.DEF_PK_TYPE = DEF_PK_TYPE
        self._con_args = kwargs
        if path:
            self.connect(path)


    def connect(self, path, fast=0, in_memory=0, isolation=None, journal=None, synchronous=None):
        """
        Connect to a DB.

        in_memory=1 causes the DB to be kept in memory; run .save_to_disk() periodically.
        isolation=None means autocommit. Set to '' for default behavior (other values: DEFERRED,
        IMMEDIATE or EXCLUSIVE).
        """
        t0 = time.time()
        self.in_memory = in_memory
        self.fast = fast
        self.journal = journal
        self.synchronous = synchronous
        self.isolation = isolation
        if self.in_memory:
            self.fast = 1
            self.path = ':memory:'
            self.realpath = path
        else:
            self.realpath = self.path = path
        if self.fast:
            if not self.journal:
                self.journal = 'OFF'
            if not self.synchronous:
                self.synchronous = 'OFF'
            if self.isolation is None:
                self.isolation = 'EXCLUSIVE'
        self.conn = sqlite3.connect(self.path, isolation_level=isolation, **self._con_args)
        # if self.in_memory:
        #    data = zlib.decompress(open(self.realpath), 'rb').read()
        self.conn.row_factory = sqlite3.Row
        self.conn.text_factory = str
        if journal:
            self.conn.execute("PRAGMA journal_mode = %s" % journal)
        if synchronous:
            self.conn.execute("PRAGMA synchronous = %s" % synchronous)
        self.cur = self.conn.cursor()
        self.connect_time = time.time() - t0
        self.dbg('DB loaded from %s in %.2fs.' % (self.realpath, self.connect_time))


    def close(self):
        if self.in_memory:
            self.save_to_disk()
        self.conn.close()


    def save_to_disk(self):
        """
        This is only needed if 'fast=1' was passed to commit (and the DB is actually kept in
        memory.
        """
        if self.in_memory:
            self.save_to_file()
        else:
            raise ValueError('save_to_disk() called for disk database!')


    def save_to_file(self, sql_filename=None, db_filename=None):
        """ Save a database to a file as SQL. Works on the current DB if none given. """
        if db_filename:
            conn = sqlite3.connect(db_filename, self._con_args)
        else:
            conn = self.conn
        sio = io.StringIO()
        for line in conn.iterdump():
            sio.write(line)
        conn.close()
        sio.seek(0)
        data = zlib.compress(sio.read())
        open(sql_filename or self.realpath, 'wb').write(data)


    def add_explicit_idpk(self, table):
        sql = self.get_table_sql(table)
        if 'primary key' in sql.lower():
            self.log('Table [%s] already has an explicit primary key: %s!' % (table, sql), 'err')
            return
        columns = ', '.join(self.get_table_columns(table))
        for q in [
                'DROP TABLE IF EXISTS $t_new_',
                'CREATE TABLE $t_new_ (id INTEGER PRIMARY KEY ASC, ' + sql.split('(', 1)[1],
                'INSERT INTO $t_new_(id, %s) SELECT rowid, %s FROM $t' % (columns, columns),
                'ALTER TABLE $t RENAME TO $t_old_',
                'ALTER TABLE $t_new_ RENAME TO $t',
                'DROP TABLE $t_old_',
                ]:
            self.execute(q.replace('$t', table))


    def vacuum(self):
        self.execute('VACUUM;')


    def table_exists(self, table):
        return bool(self.fetchone("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?;", (table,)))


    def get_table_columns(self, table):
        ### UNSAFE INTERPOLATION!
        return [e['name'] for e in self.fetchall("PRAGMA table_info(%s)" % table)]


    def get_table_sql(self, table):
        return self.fetchone("SELECT sql FROM sqlite_master WHERE tbl_name = ? AND type = 'table'", (table,))[0]


    def dump_table_heads(self, tables, entries=20):
        for t in sorted(tables):
            cnt = self.fetchone("SELECT count(1) FROM %s" % t)[0]
            self.log((' %s (%s) ' % (t, cnt)).center(100, '*') + '\n')
            lst = self.fetchall("SELECT rowid, * FROM %s LIMIT %s" % (t, entries))
            if not lst:
                self.log('No entries!\n')
                continue
            keys = lst[0].keys()
            ms = dict(zip(keys, [(max(len(k), max(len(str(lst[i][k]).strip()) for i in range(len(lst)))) + 2)
                    for k in keys]))
            hdr = '| %s |' % (' | '.join('%-*s' % (ms[ee], ee.strip()) for ee in keys))
            sep_line = '*%s*' % ('-' * (len(hdr) - 2))
            self.log(sep_line)
            self.log(hdr)
            self.log(sep_line)
            for e in lst:
                self.log('| %s |' % (' | '.join('%-*s' % (ms[ee], str(e[ee])[:50].strip()) for ee in keys)))
            self.log(sep_line)
            self.log('\n')


    def create_tables(self, tables):
        """
        Creates tables (if they don't already exist). 'tables' is a dict mapping table names to a
        valid SQL table description. E.g:

        db.create_tables({'t1':'id INTEGER PRIMARY KEY ASC, name TEXT NOT NULL',})
        """
        for table in tables:
            if not self.table_exists(table):
                self.execute("CREATE TABLE %s(%s)" % (table, tables[table].replace('${PK}', DEF_PK_TYPE)))
                self.conn.commit()


    def create_indexes(self, tables):
        """
        Ensures indexes exist on the given columns for the given tables. 'tables' is a dict mapping
        table names to a list of column names (strings).
        """
        for table in tables:
            for column in tables[table]:
                self.execute("CREATE INDEX IF NOT EXISTS index_%s ON %s (%s)" % (re.sub('[, ]+', '_',
                        column), table, column))



def backup(src_path, dest_path):
    """
    Create a backup of an sqlite database (ctypes based).
    """
    p_src_db = ctypes.c_void_p(None)
    p_dst_db = ctypes.c_void_p(None)
    null_ptr = ctypes.c_void_p(None)

    if not sqlite_dll:
        init()

    ret = sqlite_dll.sqlite3_open_v2(src_path, ctypes.byref(p_src_db), SQLITE_OPEN_READONLY, null_ptr)
    assert ret == SQLITE_OK
    assert p_src_db.value is not None
    ret = sqlite_dll.sqlite3_open_v2(dest_path, ctypes.byref(p_dst_db), SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE,
            null_ptr)
    assert ret == SQLITE_OK
    assert p_dst_db.value is not None

    p_backup = sqlite_dll.sqlite3_backup_init(p_dst_db, 'main', p_src_db, 'main')
    assert p_backup is not None

    while True:
        ret = sqlite_dll.sqlite3_backup_step(p_backup, 20)
        remaining = sqlite_dll.sqlite3_backup_remaining(p_backup)
        # pagecount = sqlite_dll.sqlite3_backup_pagecount(p_backup)
        if remaining == 0:
            break
        if ret in (SQLITE_OK, SQLITE_BUSY, SQLITE_LOCKED):
            sqlite_dll.sqlite3_sleep(100)

    sqlite_dll.sqlite3_backup_finish(p_backup)

    sqlite_dll.sqlite3_close(p_dst_db)
    sqlite_dll.sqlite3_close(p_src_db)



def init():
    """
    Initialize the ctypes wrapper over sqlite3.dll for the `backup()` function.
    """
    global sqlite_dll
    if not sqlite_dll:
        sqlite_dll = ctypes.CDLL('sqlite3.dll')
        sqlite_dll.sqlite3_backup_init.restype = ctypes.c_void_p


sqlite_dll = None
