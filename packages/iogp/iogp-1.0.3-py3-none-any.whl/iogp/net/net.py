"""
iogp.net.net: Basic network-related operations.

Todo: refactor (particularly the error / exception handling).

Author: Vlad Topan (vtopan/gmail)
"""

from ..db import DataCache, CACHE_ONLY, CACHE_ALWAYS, DEF_MAX_AGE     # NOQA

import re
import gzip
import hashlib
import io
import ssl
from urllib.request import HTTPPasswordMgrWithDefaultRealm, HTTPCookieProcessor, HTTPBasicAuthHandler, build_opener, \
    Request, HTTPSHandler
from urllib.parse import parse_qs
from http.cookiejar import LWPCookieJar


USER_AGENTS = {
    'iogp': 'Mozilla/5.0 (compatible; iogp 1.0)',
    # contemporary browsers @ 2018.10
    'chrome69-win10': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'chrome69-win7': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'chrome69-osx10': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'chrome69-linux': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    'firefox40-win7':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'firefox62-win10': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
    'firefox62-win81': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
    'firefox62-ubuntu': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0',
    'safari12-osx10': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
    'edge17-win10': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
    # old browsers
    'firefox13-win7': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.0) Gecko/20100101 Firefox/13.0.1',
    'ie6-winxp':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
    'ie7-winxp':'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; SV1)',
    'ie8-winxp':'Mozilla/4.0 (Compatible; MSIE 8.0; Windows NT 5.2; Trident/6.0)',
    'ie9-win7':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'ie9-winvista':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/4.0; GTB7.4; InfoPath.3; SV1; .NET CLR 3.1.76908; WOW64; en-US)',
    'ie10-win7':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'opera12-win7':'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00',
    # bots
    'google-bot': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'bing-bot': 'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
    'slurp-bot': 'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',
    'duck-bot': 'DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)',
    'baidu-bot': 'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
    'yandex-bot': 'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
    'facebook-bot': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
    }
USER_AGENTS[None] = USER_AGENTS['iogp']      # default

# used for a more faitful emulation of a browser's requests
GET_HEADERS = {
    'ff': '''GET /%(path)s HTTP/1.1
Host: %(domain)s
User-Agent: Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.5) Gecko/20070713 Firefox/2.0.0.5
Accept: text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5
Accept-Language: en-us,en;q=0.5
Accept-Encoding: gzip,deflate
Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7
Keep-Alive: 300
Connection: keep-alive

''',
    'ie':'''GET /%(path)s HTTP/1.1
Accept: image/gif, image/x-xbitmap, image/jpeg, image/pjpeg, application/x-shockwave-flash, */*
Accept-Language: en-us
Accept-Encoding: gzip, deflate
User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 2.0.50727; MEGAUPLOAD 1.0; FDM)
Host: %(domain)s
Connection: Keep-Alive

''',
    'opr':'''GET /%(path)s HTTP/1.1
User-Agent: Opera/9.25 (Windows NT 5.1; U; en)
Host: %(domain)s
Accept: text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1
Accept-Language: en-US,en;q=0.9
Accept-Charset: iso-8859-1, utf-8, utf-16, *;q=0.1
Accept-Encoding: deflate, gzip, x-gzip, identity, *;q=0
Connection: Keep-Alive

'''
    }


_RX = {
    'ver':(r'(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?(?:\s+\((\d+/\d+/\d+ \d+:\d+:\d+)|(\d+:\d+:\d+, \d+\.\d+\.\d+)\))?\s*(.*?)',),
    'user:pass@domain':(r'([^:]+)[:]([^@]+)@([^:]+)(?::(.+))?', re.I),
    'domain':(r'(?:[^/]+\.)*([^/]+\.[a-zA-Z]{2,5})', re.I),
    }
for k in _RX:
    _RX[k] = re.compile(*_RX[k])

__ENV_EVAL__ = {
    }

_DOWNLOAD_CACHE = None


def parse_query(query):
    """
    Parse a query string into a dict.
    """
    res = {}
    for k, v in parse_qs(query).items():
        if isinstance(k, bytes):
            k = k.decode('ascii', 'ignore')
        v = v[0]
        if isinstance(v, bytes):
            v = v.decode('ascii', 'ignore')
        res[k] = v
    return res


def load_cookies(filename):
    """
    Load cookies from file.
    """
    return LWPCookieJar(filename)


def download(url, referer=None, cache=DEF_MAX_AGE, headers=None, cookies=None, auth=None, nocert=False,
            post_data=None, timeout=10, user_agent=None, max_size=None, info=None, ignore_404=True,
            debug=0):
    """
    Download from a URL.

    Todo: logging callback.

    :param auth: Tuple (user, password).
    :param cookies: Jar filename which can be loaded with load_cookies().
    :param headers: dict containing additional headers.
    :param max_size: integer or a (callback) function taking an integer which return True to download.
    :param info: dict which, if given, will be filled in with download info.
    :param nocert: Don't verify server SSL certificate.
    :return: Data as `bytes` (pass the `info` dict to get a HTTP 'code' field and response headers under 'headers').
    """
    if info is None:
        info = {}
    info['error'] = None
    # print(f'[GET] {cache} {url}')
    if cache:
        if _DOWNLOAD_CACHE is None:
            init()
        post_hash = hashlib.md5(post_data if type(post_data) == bytes else str(post_data).encode('utf8')).hexdigest() \
            if post_data else ''
        cache_url = url + post_hash
        data = _DOWNLOAD_CACHE.get(cache_url, cache)
        if data:
            # print(f'Cache hit: {url}')
            return data
        else:
            # print(f'Cache miss: {url}')
            if cache == CACHE_ONLY:
                return None
            pass
    else:
        data = None
    # prepare handlers
    handlers = []
    if cookies is not None:
        handlers.append(HTTPCookieProcessor(cookies))
    if auth:
        # fixme
        toplevel = ('/'.join(url.split('/', 4)[:3]) if '://' in url else ('http://' + url.split('/', 1)[0])) + '/'
        pwmgr = HTTPPasswordMgrWithDefaultRealm()
        user, psw = auth
        pwmgr.add_password(None, toplevel, user, psw)
        handlers.append(HTTPBasicAuthHandler(pwmgr))
    if nocert:
        handlers.append(HTTPSHandler(context=ssl._create_unverified_context()))
    # create opener
    opener = build_opener(*handlers)
    # prepare headers
    if user_agent in USER_AGENTS:
        user_agent = USER_AGENTS[user_agent]
    opener.addheaders = [('User-agent', user_agent)]
    if referer:
        opener.addheaders.append(('Referer', referer))
    for k, v in (headers or {}).items():
        opener.addheaders.append((k, v))
    resp = None
    try:
        # if post_data and type(post_data) != bytes:
        #    post_data = urlencode(post_data).encode('ascii')
        req = Request(url, data=post_data)
        if debug:
            print(f' * net.download({url})')
        resp = opener.open(req, timeout=timeout)
        info['code'] = resp.getcode()
        info['headers'] = resp_info = dict(resp.info())
        if max_size and 'Content-Length' in resp_info:
            # try:
                content_size = int(resp_info['Content-Length'])
                if hasattr(max_size, '__call__'):
                    if not max_size(content_size):
                        return None
                elif content_size > max_size:
                    return None
            # except:
                # [todo] fixme
                # pass
        data = resp.read()
    except Exception as e:
        # fixme
        # if not (ignore_404 and ('urlopen error timed out' in str(e) or \
        #        'getaddrinfo failed' in str(e) or '404' in str(e))):
        info['error'] = str(e)
        print('EXCEPTION: %s' % str(e))
        import traceback
        traceback.print_exc(5)
        return None
    if cookies is not None:
        cookies.extract_cookies(resp, req)
    if data.startswith(b'\x1F\x8B\x08\0\0\0\0\0'):
        data = gzip.decompress(data)
    if data and cache:
        _DOWNLOAD_CACHE[cache_url] = data
    return data


def init(filename='.url-cache.db'):
    global _DOWNLOAD_CACHE
    _DOWNLOAD_CACHE = DataCache(filename)

