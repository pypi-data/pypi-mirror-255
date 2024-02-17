"""
iogp.db.dbobj: Generic DB object wrapper (to be inherited by specific DB wrappers such as sqlite).

Author: Vlad Topan (vtopan/gmail)
"""

import inspect
import time
import sys
import threading


# in queries
PARAM = '?'
DEF_ID_KEY_PAT = '${KEY}'



class GenDBObj(object):
    """
    Generic DB (conn+cursor) object.

    :param log_all: Log all queries.
    :param cacheable: List of table names whose entries are cached.
    """

    def __init__(self, warn_long_time=2, time_queries=0, debug=0, log_all=0, cacheable=None,
                serialized=False, **kwarg):
        self.warn_long_time = warn_long_time
        self.log_all = log_all
        self.time_queries = time_queries
        self.cache = {}
        self.qtimes = {}
        self.debug = debug
        self.conn = self.cur = None
        self.serialized = serialized
        self.lock = threading.Lock()
        self.cacheable = cacheable if cacheable is not None else []


    def commit(self):
        if self.conn:
            self.conn.commit()


    def execute(self, query, args=None, log=0):
        if self.serialized:
            self.lock.acquire()
        query = query.replace(PARAM, self.ISYM).replace(DEF_ID_KEY_PAT, self.DEF_ID_KEY)
        if log or self.log_all:
            self.log('[DBG] QUERY [%s]; ARGS [%s]\n' % (query, args))
        t0 = time.time()
        try:
            self.cur.execute(query, args or [])
        except:     # fixme!
            self.log("QUERY [%s]; ARGS [%s] failed!" % (query, args))
            if self.serialized:
                self.lock.release()
            raise
        delta = time.time() - t0
        if self.warn_long_time and delta > self.warn_long_time:
            self.log('[DBG] Query [%s] took %5.2fs\n' % (query, delta), 'warn')
        if self.time_queries:
            k = '%-20s %s' % (caller()[:20], query[:80])
            if k not in self.qtimes:
                self.qtimes[k] = [1, delta]
            else:
                self.qtimes[k][0] += 1
                self.qtimes[k][1] += delta
        if self.serialized:
            self.lock.release()


    def executemany(self, query, args):
        if self.serialized:
            self.lock.acquire()
        self.conn.executemany(query, args)
        if self.serialized:
            self.lock.release()


    def fetchall(self, query, args=None, log=0, **kargs):
        self.execute(query, args, log=log, **kargs)
        return self.cur.fetchall()


    def fetchone(self, query, args=None, log=0, **kargs):
        self.execute(query, args, log=log, **kargs)
        res = self.cur.fetchone()
        if log or self.log_all:
            self.log('=> %s\n' % (res,))
        return res


    def fetchvalue(self, query, args=None, log=0, **kargs):
        res = self.fetchone(query, args=args, log=log, **kargs)
        if res:
            res = res[0]
        return res


    def fetchmany(self, count, query, args=None, log=0, **kargs):
        self.execute(query, args, log=log, **kargs)
        return self.cur.fetchmany(count)


    def get_id(self, val, table, col_val='name', col_key=None, insert=1, case_sens=1, log=0):
        """
        Get the ID (key) of a value (assuming key/value as (row)id/name).
        """
        if type(val) is not tuple:
            val = (val,)
        if col_key is None:
            col_key = self.DEF_ID_KEY
        op = '=' if case_sens else 'LIKE'
        ckey = '%s%s%s' % (col_val, col_key, val)
        if table in self.cacheable and table in self.cache and ckey in self.cache[table]:
            return self.cache[table][ckey]
        sel_col_val = ' AND '.join('%s %s ?' % (x.strip(), op,) for x in col_val.split(','))
        res = self.fetchone("SELECT %s FROM %s WHERE %s" % (col_key, table, sel_col_val), val, log=log)
        if (not res) or res[0] is None:
            if insert:
                ins_col_val = ','.join('?' * len(val))
                self.execute("INSERT INTO %s(%s) VALUES(%s)" % (table, col_val, ins_col_val), val, log=log)
                self.commit()
                res = self.fetchvalue("SELECT %s FROM %s WHERE %s" % (col_key, table, sel_col_val), val, log=log)
            else:
                res = None
        else:
            res = res[0]
        if res is not None and table in self.cacheable:
            if table not in self.cache:
                self.cache[table] = {}
            self.cache[table][ckey] = res
        return res


    def get_value(self, key, table, col_val='name', col_key=None, log=0):
        """
        Get the value for the given ID (key).
        """
        if type(key) is not tuple:
            key = (key,)
        ckey = '%s%s%s' % (key, col_val, col_key)
        if col_key is None:
            col_key = self.DEF_ID_KEY
        if col_key == self.DEF_ID_KEY and table in self.cacheable and table in self.cache and ckey in self.cache[table]:
            return self.cache[table][ckey]
        col_key = ' AND '.join('%s %s' % (x.strip(), '= ?' if key[i] is not None else 'IS NULL')
                for i, x in enumerate(col_key.split(',')))
        res = self.fetchone("SELECT %s FROM %s WHERE %s" % (col_val, table, col_key), [x for x in key if x is not None],
                log=log)
        if res and len(res) == 1:
            res = res[0]
        if log:
            print(' => %s' % res)
        if table in self.cacheable:
            if table not in self.cache:
                self.cache[table] = {}
            self.cache[table][ckey] = res
        return res


    def insert(self, table, fields, keyColumns=('name',), update=1, no_id_key=False, log=0):
        if type(keyColumns) is str:
            keyColumns = (keyColumns,)
        where = ' AND '.join('%s = ?' % (x,) for x in keyColumns)
        keys = tuple([fields[x] for x in keyColumns])
        retkey = ', '.join(keyColumns) if no_id_key else self.DEF_ID_KEY
        rid = self.fetchvalue("SELECT %s FROM %s WHERE %s" % (retkey, table, where), keys, log=log)
        if rid is not None:
            # self.log(' * Known %s: %s; update? :-?' % (keyColumns, keys))
            if update:
                tfields = ', '.join("%s = ?" % (k,) for k in fields)
                self.execute("UPDATE %s SET %s WHERE %s" % (table, tfields, where),
                        tuple(fields.values()) + keys)
        else:
            self.execute("INSERT INTO %s (%s) VALUES (%s)" % (table,
                    ', '.join(fields), ', '.join('?' for x in fields)), fields.values(), log=log)
            rid = self.fetchvalue("SELECT %s FROM %s WHERE %s" % (retkey, table, where), keys, log=log)
        self.conn.commit()
        return rid


    def table_exists(self, table):
        raise NotImplementedError("%s() not implemented!" % inspect.stack()[0][3])


    def constraint_exists(self, constraint):
        raise NotImplementedError("%s() not implemented!" % inspect.stack()[0][3])


    def get_table_columns(self, table):
        raise NotImplementedError("%s() not implemented!" % inspect.stack()[0][3])


    def get_table_sql(self, table):
        raise NotImplementedError("%s() not implemented!" % inspect.stack()[0][3])


    def dump_table_heads(self, tables, entries=20):
        raise NotImplementedError("%s() not implemented!" % inspect.stack()[0][3])


    def create_tables(self, tables):
        raise NotImplementedError("%s() not implemented!" % inspect.stack()[0][3])


    def create_indexes(self, tables):
        raise NotImplementedError("%s() not implemented!" % inspect.stack()[0][3])


    def create_pks(self, pks):
        for table, keys in pks.items():
            name = 'pk_%s' % (table,)
            if not self.constraint_exists(name):
                self.log('Creating PK %s...\n' % name)
                self.execute("ALTER TABLE %s ADD CONSTRAINT %s PRIMARY KEY (%s)" % (table, name, ', '.join(keys)),
                        log=1)


    def dbg(self, msg):
        """
        Print debug message.
        """
        self.log(msg, 'dbg')


    def log(self, msg, mt='info'):
        """
        Print message.
        """
        if self.debug or (mt != 'dbg'):
            sys.stdout.write(msg)


    def dump_qtimes(self, maxlen=100):
        self.log('%-*s  %-6s  %s\n' % (maxlen, 'Query', 'Count', 'Time (s)'))
        for k, v in sorted(self.qtimes.items(), key=lambda x:x[1][1], reverse=1):
            self.log('%-*s  %-6d  %.2f\n' % (maxlen, k[:maxlen], v[0], v[1]))



def caller(fun=None):
    depth = 1 if fun else 2
    return inspect.stack()[depth][3]

