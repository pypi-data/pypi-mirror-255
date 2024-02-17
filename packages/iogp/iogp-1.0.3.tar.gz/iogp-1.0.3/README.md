# iogp

Python common task, general purpose library (serialization, networking, etc.).
Note: this project used to be called iolib - it was renamed for PyPI.

## iogp.net

- provides the `download()` function
    - automatic caching of downloads
    - supports cookies, authentication, etc.
    - can spoof user agents (or the entire GET request) - see the `USER_AGENTS` dict in `net/net.py`
    - examples:
        - `text = iogp.net.download('https://google.com')`
        - `info = {}; iogp.net.download('https://1.1.1.1', info=info, cache=0)` => `info['code'] == 200`,
            `info['headers']['Content-Type']`, etc.


## iogp.db

- provides a persistence / caching / storage object `DataCache` that can store e.g. the results from a downloaded URL
    - use `DataStore` to also get in-memory caching of values
    - `ObjCache()` wraps `DataCache` to generate the storage filename automatically
    - usage:

        ~~~Python
        from iogp.db import DataCache

        fn = 'objects.db'

        db = DataCache(fn)
        db['key1'] = {'some':['serializable', 'object', 0]}
        db['some-other-key'] = 0
        db.close()

        db = DataCache(fn)
        print(db['key1'])
        print('key2' in db, 'some-other-key' in db)
        ~~~


## iogp.win

- ctypes wrapper over some Windows-specific functions
- example - iterating all windows and retrieving the window title for each one:

    ~~~Python
    import iogp.win as win
    
    def callback(hwnd, lparam):
        size = 512
        buf = win.unicode_buffer(size)
        win.GetWindowText(hwnd, buf, size)
        print(f'[-] Handle: {hwnd}, title: {buf.value}')
        return 1  # 0 to stop
        
    win.EnumWindows(win.WNDENUMPROC(callback), 0)
    ~~~
