import time
import os
import sys
import gzip
import traceback

v = sys.version_info[0]

if v == 2:
    from StringIO import StringIO
    import urllib2 as ul
else:
    import urllib.request as ul



header_file = 'headers.txt'

LINES_PER_BLOCK = 500
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


def flush_info(writing_dir, info, delete = False):
    court_id = info['court_id']
    court_dir = writing_dir + os.sep + str(court_id)
    if not os.path.isdir(court_dir):
        os.mkdir(court_dir)
    elif delete:
        ffs = os.listdir(court_dir)
        for ff in ffs:
            os.remove(os.path.join(court_dir, ff))
    f = open(court_dir + os.sep + "info.txt", 'w')
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


def current_progress(year_dir, case_type, judge_type):
    court_id = fetch_court(year_dir, case_type, judge_type)
    working_dir = "%s/%s_%s" % (year_dir, case_type, judge_type)
    info = read_info(working_dir, court_id)
    return str(info)


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
            return str(data, 'utf-8')
    else:
        return data


def get_resp(url, add_headers = {}, proxy = {}):
    """cookies added to headers"""
    req = ul.Request(url, headers=add_headers)
    if proxy:
        proxy_support = ul.ProxyHandler(proxy)
        opener = ul.build_opener(proxy_support)
        ul.install_opener(opener)
    return ul.urlopen(req, timeout=30)


def request_with_proxy(url, add_headers = {}, proxy = {}):
    resp = get_resp(url, add_headers, proxy)
    result = decompress_response(resp)
    return result


def fetch_cookie(proxy_pool = None):
    headers = load_header()
    if proxy_pool:
        proxy = proxy_pool.get_random()
        while proxy:
            try:
                resp = get_resp('https://www.itslaw.com/api/v1/users/user/loginInfo', headers, proxy= {'https':proxy})
                proxy_pool.confirm_success(proxy)
                sys.stdout.write(proxy + " ok!\n")
                break
            except Exception as e:
                sys.stdout.write(proxy + " failed!\n")
                sys.stdout.flush()
                proxy_pool.confirm_fail(proxy)
                print(e)
                proxy = proxy_pool.get_random()

    else:
        resp = get_resp('https://www.itslaw.com/api/v1/users/user/loginInfo', headers)
    new_cookie = resp.info().get('set-cookie')
    old_cookie = headers['Cookie']
    sys.stdout.write("%s => %s\n" % (old_cookie, new_cookie))
    if not new_cookie is None: #new session
        new_cookies = dict([kv.strip().split("=") for kv  in  new_cookie.split(';')])
        old_cookies = dict([kv.strip().split("=") for kv  in  old_cookie.split(';')])
        new_cookies.pop("Path")
        old_cookies.update(new_cookies)
        headers['Cookie'] = '; '.join(["%s=%s" % d for d in old_cookies.items()])
        update_header(headers)


def save_courts(year_dir, case_type, judge_type, info, update = False):
    courts_file = year_dir + os.sep + "%s_%s.court" %(case_type, judge_type)

    if update:
        f = open(courts_file)
        lines = f.read().strip().split('\n')
        for idx, line in enumerate(lines):
            info_here = line.split('\t')
            if int(info_here[0]) == info['court_id']:
                sys.stdout.write("save: " + str(info['court_id']) + "\n")
                sys.stdout.flush()
                break
        info_here[1] = str(info['finished_idx'])
        info_here[4] = '1'
        info_here[3] = "%.3f" % ((info['finished_idx'] if info['finished_idx'] > 0 else 0) / (float(info_here[2]) + 0.00000000000001))
        lines[idx] = '\t'.join(info_here)
        f.close()
        f = open(courts_file, 'w')
        f.write('\n'.join(lines) + "\n")
        f.close()

    else:
        new_line = "%d\t%d\t%d\t%.3f\t0\n" % (info['court_id'], info['finished_idx'], info['total_count'],
                                              (info['finished_idx'] if info['finished_idx'] > 0 else 0) / (
                                              info['total_count'] + 0.00000000000001))
        f = open(courts_file , 'a')
        sys.stdout.write("save: " + str(info['court_id']) + "\n")
        sys.stdout.flush()
        f.write(new_line)
        f.close()


def fetch_court(year_dir, case_type, judge_type, goto_end = False):
    courts_file = year_dir + os.sep + "%s_%s.court" % (case_type, judge_type)
    if not os.path.isfile(courts_file):
        f = open(courts_file, 'w')
        f.close()
    f = open(courts_file)
    last_court = ''
    for line in f:
        court_id, fi, tc, ratio, fh = line.split()
        # court_id, fi, tc, ratio,fh =
        last_court = court_id
        if fh == '0' and not tc == '0' and not goto_end:
            return int(last_court)
    f.close()
    if last_court and goto_end: #for the crawl_courts()
        return int(last_court)
    elif last_court:  # for courtid boundary fetch
        return 0
    return 1 # not inited


if __name__ == '__main__':
    fetch_cookie()