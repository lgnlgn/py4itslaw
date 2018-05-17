import time
import os
import sys
import gzip


v = sys.version_info[0]

if v == 2:
    from StringIO import StringIO
    import urllib2 as ul
else:
    import urllib.request as ul



header_file = 'headers.txt'
LINES_PER_BLOCK = 100
TIME_EXPIRE_SEC = 3600
crawling_info = {'court_id': 0,'total_count': -1, 'finished_idx': 0, 'next_idx': 0, 'next_docid': '', 'next_area': '0'}


def load_header():
    with open( header_file) as f:
        hh = f.read()
    return dict([h.strip().split(":", 1) for h in hh.strip().split('\n')])


def update_header(headers = {}):
    if not headers:
        headers = load_header()
    headers['time'] =  str(int(time.time()))
    with open(header_file, 'w') as f:
        for k, v in headers.items():
            f.write("%s:%s\n" % (k, v))


def update_info( info, next_docid, next_area):
    """updates info; +1 to idx then save {} to info.txt"""
    info['next_docid'] = next_docid
    info['next_area'] = next_area
    info['next_idx'] += 1
    info['finished_idx'] += 1
    info['time'] = time.asctime()
    return info


def flush_info(writing_dir, info):
    court_id = info['court_id']
    f = open(writing_dir + os.sep + str(court_id) + os.sep + "info.txt", 'w')
    f.write(str(info))
    f.close()


def write_down(writing_dir, content, next_idx):
    block_id = int((next_idx - 1) / LINES_PER_BLOCK)
    if v == 2:
        f = open(writing_dir + os.sep + str(block_id), 'a')
    else:
        f = open(writing_dir + os.sep + str(block_id), 'a', encoding='utf-8')
    f.write(content + "\n")
    f.close()

def get_minmax_courts(working_dir):
    """
        get max_court_id & create a new info.txt
    """
    courts = os.listdir(working_dir)
    if len(courts) == 0:
        return 0, 3568
    # get last court
    already_downed = list(map(int, filter(str.isdigit, courts)))
    return min(already_downed), max(already_downed)   # check again without else


def create_info(working_dir, court_id):
    court_dir = working_dir + os.sep + str(court_id)
    info_path = court_dir + os.sep + "info.txt"
    if not os.path.isdir(court_dir):
        os.mkdir(court_dir)   # ensure dir exits
    if not os.path.isfile(info_path):
        ci = {}
        ci.update(crawling_info)
        ci['court_id'] = court_id
        flush_info(working_dir, ci)


def read_info(working_dir, court_id):
    """ reads from info.txt"""
    court_dir = working_dir + os.sep + str(court_id)
    info_path = court_dir + os.sep + "info.txt"
    if not os.path.isdir(court_dir) or not os.path.isfile(info_path):
        return None
    while True:
        try:
            f = open(info_path)
            cc = eval(f.read())
            f.close()
            return cc
        except:
            sys.stdout.write(" read info error !!!!!! sleep 50ms")
            time.sleep(0.02)


def current_progress(working_dir):
    a,b = get_minmax_courts(working_dir)
    info = read_info(working_dir, b)
    return str(info)


def ck_deprecated():
    headers = load_header()
    tm = headers.get('time')
    tm2 = tm
    cookies = headers.setdefault("Cookie","Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c=1520693568").split('; ')
    vv = filter(lambda x : x[1].isdigit(),  [x.split('=') for x in cookies])
    for v in vv :
        tm2 = v[1]

    tm = max(tm, tm2) if tm else tm2
    return True if time.time() - int(tm) > TIME_EXPIRE_SEC else False

def decompress_response(response):
        data = response.read() # reads
        if response.info().get('Content-Encoding') == 'gzip':
            if v == 2:
                buf = StringIO(data)
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
            else:
                data = gzip.decompress(data).decode("utf-8")
            return data
        elif type(data) == bytes:
            if v == 2:
                return str(data)
            else:
                return str(data, encoding='utf-8')
        return data

def get_resp(url, add_headers = {}, proxy = {}):
    """cookies added to headers"""
    req = ul.Request(url, headers=add_headers)
    if proxy:
        proxy_support = ul.ProxyHandler(proxy)
        opener = ul.build_opener(proxy_support)
        ul.install_opener(opener)
    return ul.urlopen(req, timeout=60)


def request_with_proxy(url, add_headers = {}, proxy = {}):
    return decompress_response(get_resp(url, add_headers, proxy))


def fetch_cookie(proxy = {}):
    headers = load_header()
    resp = get_resp('https://www.itslaw.com/api/v1/users/user/loginInfo', headers, proxy= proxy)
    new_cookie = resp.info()['set-cookie']
    old_cookie = headers['Cookie']
    sys.stdout.write("%s => %s\n" % (old_cookie, new_cookie))
    new_cookies = dict([kv.strip().split("=") for kv  in  new_cookie.split(';')])
    old_cookies = dict([kv.strip().split("=") for kv  in  old_cookie.split(';')])
    new_cookies.pop("Path")
    old_cookies.update(new_cookies)
    headers['Cookie'] = '; '.join(["%s=%s" % d for d in old_cookies.items()])
    update_header(headers)
